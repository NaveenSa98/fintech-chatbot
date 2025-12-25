import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { Box, Flex } from "@chakra-ui/react"
import { AuthProvider } from "./context/AuthContext"
import Login from "./pages/Login"
import Home from "./pages/Home"
import Chat from "./pages/Chat"
import Documents from "./pages/Documents"
import Profile from "./pages/Profile"
import ProtectedRoute from "./components/ProtectedRoute"
import Header from "./components/Header"
import Footer from "./components/Footer"
import Sidebar from "./components/Sidebar"

function App() {
  return (
    <AuthProvider>
      <Router>
        <Flex minH="100vh" flexDirection="column" bg="gray.50">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/*"
              element={
                <Flex flexDirection="column" flex={1} w="full">
                  <Header />
                  <Flex flex={1} overflow="hidden">
                    <Sidebar />
                    <Box flex={1} display="flex" flexDirection="column" overflowY="auto">
                      <Routes>
                        <Route
                          path="/"
                          element={
                            <ProtectedRoute>
                              <Home />
                            </ProtectedRoute>
                          }
                        />
                        <Route
                          path="/chat"
                          element={
                            <ProtectedRoute>
                              <Chat />
                            </ProtectedRoute>
                          }
                        />
                        <Route
                          path="/documents"
                          element={
                            <ProtectedRoute>
                              <Documents />
                            </ProtectedRoute>
                          }
                        />
                        <Route
                          path="/profile"
                          element={
                            <ProtectedRoute>
                              <Profile />
                            </ProtectedRoute>
                          }
                        />
                        <Route path="*" element={<Navigate to="/" replace />} />
                      </Routes>
                    </Box>
                  </Flex>
                  <Footer />
                </Flex>
              }
            />
          </Routes>
        </Flex>
      </Router>
    </AuthProvider>
  )
}

export default App
