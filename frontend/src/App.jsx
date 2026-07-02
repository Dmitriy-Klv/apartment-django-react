import { Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from '@/components/routing/ProtectedRoute'
import { RoleRoute } from '@/components/routing/RoleRoute'
import { HomePage } from '@/pages/HomePage'
import { LessorBookingsPage } from '@/pages/LessorBookingsPage'
import { ListingDetailPage } from '@/pages/ListingDetailPage'
import { ListingFormPage } from '@/pages/ListingFormPage'
import { ListingsPage } from '@/pages/ListingsPage'
import { LoginPage } from '@/pages/LoginPage'
import { MyBookingsPage } from '@/pages/MyBookingsPage'
import { MyListingsPage } from '@/pages/MyListingsPage'
import { ProfilePage } from '@/pages/ProfilePage'
import { RegisterPage } from '@/pages/RegisterPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route path="/listings" element={<ListingsPage />} />
      <Route path="/listings/:id" element={<ListingDetailPage />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/profile" element={<ProfilePage />} />
      </Route>

      <Route element={<RoleRoute role="tenant" />}>
        <Route path="/my-bookings" element={<MyBookingsPage />} />
      </Route>

      <Route element={<RoleRoute role="lessor" />}>
        <Route path="/my-listings" element={<MyListingsPage />} />
        <Route path="/listings/new" element={<ListingFormPage />} />
        <Route path="/listings/:id/edit" element={<ListingFormPage />} />
        <Route path="/lessor/bookings" element={<LessorBookingsPage />} />
      </Route>
    </Routes>
  )
}

export default App
