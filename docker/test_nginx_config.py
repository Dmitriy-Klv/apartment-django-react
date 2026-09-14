import re
from pathlib import Path

DOCKER_DIR = Path(__file__).resolve().parent
NGINX_CONF = (DOCKER_DIR / 'nginx.conf').read_text(encoding='utf-8')
NGINX_HTTPS_SH = (DOCKER_DIR / 'nginx-https.sh').read_text(encoding='utf-8')

HEADER_VALUES = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
}

CSP_DIRECTIVES = [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "font-src 'self'",
    "connect-src 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "object-src 'none'",
]


def extract_ssl_server_block(script: str) -> str:
    """Return the body of the `listen 443 ssl` server block from nginx-https.sh."""
    match = re.search(r'listen 443 ssl;.*?\n}\n', script, re.DOTALL)
    assert match, 'listen 443 ssl block not found in nginx-https.sh'
    return match.group(0)


def extract_http_redirect_block(script: str) -> str:
    """Return the body of the plain HTTP redirect-to-HTTPS server block."""
    match = re.search(r'listen 80;.*?location / \{\s*return 301.*?\n    \}\n\}\n', script, re.DOTALL)
    assert match, 'HTTP redirect block not found in nginx-https.sh'
    return match.group(0)


def extract_acme_bootstrap_block(script: str) -> str:
    """Return the ACME-only bootstrap block used before a certificate exists."""
    parts = script.split('else')
    assert len(parts) == 2, 'expected exactly one if/else branch in nginx-https.sh'
    return parts[1]


class TestHttpServerHeaders:

    def test_content_type_options_present(self):
        """Plain-HTTP server must send X-Content-Type-Options: nosniff."""
        assert 'add_header X-Content-Type-Options "nosniff" always;' in NGINX_CONF

    def test_frame_options_present(self):
        """Plain-HTTP server must deny framing via X-Frame-Options."""
        assert 'add_header X-Frame-Options "DENY" always;' in NGINX_CONF

    def test_referrer_policy_present(self):
        """Plain-HTTP server must send a strict Referrer-Policy."""
        assert 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;' in NGINX_CONF

    def test_csp_present_with_all_directives(self):
        """Plain-HTTP server must send a Content-Security-Policy covering every directive."""
        match = re.search(r'add_header Content-Security-Policy "([^"]+)" always;', NGINX_CONF)
        assert match, 'Content-Security-Policy header not found in nginx.conf'
        policy = match.group(1)
        for directive in CSP_DIRECTIVES:
            assert directive in policy

    def test_hsts_not_sent_over_plain_http(self):
        """Strict-Transport-Security must never be sent without TLS (RFC 6797)."""
        assert 'Strict-Transport-Security' not in NGINX_CONF

    def test_existing_robots_header_untouched(self):
        """The pre-existing X-Robots-Tag header must survive this change."""
        assert 'add_header X-Robots-Tag "noindex, nofollow, noarchive, nosnippet" always;' in NGINX_CONF


class TestHttpsSslServerHeaders:

    ssl_block = extract_ssl_server_block(NGINX_HTTPS_SH)

    def test_hsts_present_with_include_subdomains(self):
        """The TLS server block must send a long-lived HSTS header."""
        assert 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;' in self.ssl_block

    def test_content_type_options_present(self):
        """The TLS server block must send X-Content-Type-Options: nosniff."""
        assert 'add_header X-Content-Type-Options "nosniff" always;' in self.ssl_block

    def test_frame_options_present(self):
        """The TLS server block must deny framing via X-Frame-Options."""
        assert 'add_header X-Frame-Options "DENY" always;' in self.ssl_block

    def test_referrer_policy_present(self):
        """The TLS server block must send a strict Referrer-Policy."""
        assert 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;' in self.ssl_block

    def test_csp_present_with_all_directives(self):
        """The TLS server block must send a Content-Security-Policy covering every directive."""
        match = re.search(r'add_header Content-Security-Policy "([^"]+)" always;', self.ssl_block)
        assert match, 'Content-Security-Policy header not found in the TLS server block'
        policy = match.group(1)
        for directive in CSP_DIRECTIVES:
            assert directive in policy

    def test_existing_robots_header_untouched(self):
        """The pre-existing X-Robots-Tag header must survive this change."""
        assert 'add_header X-Robots-Tag "noindex, nofollow, noarchive, nosnippet" always;' in self.ssl_block


class TestHeadersOnlyOnContentServingBlocks:

    def test_hsts_appears_exactly_once_in_https_script(self):
        """HSTS must only be added to the TLS block, never duplicated."""
        assert NGINX_HTTPS_SH.count('Strict-Transport-Security') == 1

    def test_csp_appears_exactly_once_in_https_script(self):
        """The CSP header must only be added to the TLS block, never duplicated."""
        assert NGINX_HTTPS_SH.count('Content-Security-Policy') == 1

    def test_http_redirect_block_has_no_security_headers(self):
        """The bare 301-redirect-to-HTTPS block must stay minimal."""
        redirect_block = extract_http_redirect_block(NGINX_HTTPS_SH)
        assert 'add_header' not in redirect_block

    def test_acme_bootstrap_block_has_no_security_headers(self):
        """The pre-certificate ACME-challenge-only block must stay minimal."""
        bootstrap_block = extract_acme_bootstrap_block(NGINX_HTTPS_SH)
        assert 'add_header' not in bootstrap_block


class TestHeaderSyntax:

    def test_every_add_header_directive_uses_always(self):
        """Every add_header in both files must use `always` so it applies on error responses too."""
        for source in (NGINX_CONF, NGINX_HTTPS_SH):
            for line in source.splitlines():
                stripped = line.strip()
                if stripped.startswith('add_header'):
                    assert stripped.endswith('always;'), stripped

    def test_script_src_has_no_unsafe_directives(self):
        """script-src must stay strict; unsafe-inline/unsafe-eval are an XSS risk."""
        for source in (NGINX_CONF, NGINX_HTTPS_SH):
            match = re.search(r'add_header Content-Security-Policy "([^"]+)" always;', source)
            assert match
            script_src = re.search(r"script-src ([^;]+);", match.group(1)).group(1)
            assert 'unsafe-inline' not in script_src
            assert 'unsafe-eval' not in script_src
