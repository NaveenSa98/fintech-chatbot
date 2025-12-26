"use client"

import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputRightElement,
  VStack,
  Grid,
  GridItem,
  Text,
  Container,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Select,
  Checkbox,
  useToast,
  IconButton,
} from "@chakra-ui/react"
import { useState } from "react"
import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../hooks/useAuth"
import { authAPI } from "../services/api"

const ROLES = ["Finance", "Marketing", "HR", "Engineering", "Employee", "C-Level"]
const DEPARTMENTS = ["Finance", "Marketing", "HR", "Engineering", "General", "Administration"]

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const toast = useToast()

  // Login form state
  const [loginEmail, setLoginEmail] = useState("")
  const [loginPassword, setLoginPassword] = useState("")
  const [showLoginPassword, setShowLoginPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)

  // Register form state
  const [regFullName, setRegFullName] = useState("")
  const [regEmail, setRegEmail] = useState("")
  const [regPassword, setRegPassword] = useState("")
  const [regConfirmPassword, setRegConfirmPassword] = useState("")
  const [showRegPassword, setShowRegPassword] = useState(false)
  const [showRegConfirmPassword, setShowRegConfirmPassword] = useState(false)
  const [regRole, setRegRole] = useState("Employee")
  const [regDepartment, setRegDepartment] = useState("Administration")
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    if (!loginEmail || !loginPassword) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        status: "error",
        duration: 3000,
      })
      return
    }

    setLoading(true)
    try {
      const response = await authAPI.login(loginEmail, loginPassword)

      const user = {
        id: response.user.id,
        email: response.user.email,
        fullName: response.user.full_name,
        role: response.user.role as "Finance" | "Marketing" | "HR" | "Engineering" | "Employee" | "C-Level",
        department: response.user.department,
        status: "active" as const,
      }

      login(user, response.access_token, rememberMe)

      toast({
        title: "Success",
        description: `Welcome back, ${user.fullName}!`,
        status: "success",
        duration: 2000,
      })

      navigate("/")
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || "Login failed. Please try again."
      toast({
        title: "Error",
        description: errorMessage,
        status: "error",
        duration: 3000,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async () => {
    if (!regFullName || !regEmail || !regPassword || !regConfirmPassword) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        status: "error",
        duration: 3000,
      })
      return
    }

    if (regPassword !== regConfirmPassword) {
      toast({
        title: "Error",
        description: "Passwords do not match",
        status: "error",
        duration: 3000,
      })
      return
    }

    if (regPassword.length < 8) {
      toast({
        title: "Error",
        description: "Password must be at least 8 characters",
        status: "error",
        duration: 3000,
      })
      return
    }

    setLoading(true)
    try {
      const finalDepartment = regRole === "C-Level" ? "Administration" : regDepartment

      const response = await authAPI.register(regEmail, regPassword, regFullName, regRole, finalDepartment)

      // Check if registration was successful (response contains user id)
      if (response && response.id) {
        toast({
          title: "Success! 🎉",
          description: "Account created successfully! Please log in with your credentials.",
          status: "success",
          duration: 3000,
          isClosable: true,
        })

        // Pre-fill login email and clear form
        setLoginEmail(regEmail)
        setLoginPassword("")

        // Reset registration form
        setRegFullName("")
        setRegEmail("")
        setRegPassword("")
        setRegConfirmPassword("")
        setRegRole("Employee")
        setRegDepartment("General")

        // Redirect to login page
        setTimeout(() => {
          window.location.href = "/login"
        }, 1000)
      } else {
        throw new Error("Registration response invalid")
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || "Registration failed. Please try again."
      toast({
        title: "Registration Failed",
        description: errorMessage,
        status: "error",
        duration: 4000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box minH="100vh" bg="linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)" py={20} display="flex" alignItems="center" justifyContent="center">
      <Container maxW="md">
        <Box
          bg="white"
          borderRadius="2xl"
          boxShadow="0 20px 60px rgba(0, 0, 0, 0.3)"
          p={10}
          border="1px solid #e8f0f7"
        >
          {/* Logo/Title */}
          <Box textAlign="center" mb={10}>
            <Box
              fontSize="3xl"
              fontWeight="900"
              bg="linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)"
              bgClip="text"
              color="transparent"
              mb={2}
            >
              FinTech
            </Box>
            <Text fontSize="sm" color="gray.600" fontWeight="500">
              Enterprise AI Assistant
            </Text>
          </Box>

          <Tabs isFitted variant="soft-rounded" colorScheme="blue">
            <TabList mb={8} bg="gray.100" p={1} borderRadius="lg">
              <Tab
                fontSize="sm"
                fontWeight="600"
                _selected={{ bg: "white", boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)" }}
              >
                Login
              </Tab>
              <Tab
                fontSize="sm"
                fontWeight="600"
                _selected={{ bg: "white", boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)" }}
              >
                Register
              </Tab>
            </TabList>

            <TabPanels>
              {/* Login Tab */}
              <TabPanel>
                <VStack spacing={6}>
                  <FormControl isRequired>
                    <FormLabel fontSize="sm" fontWeight="600" color="gray.700" mb={2}>
                      Email Address
                    </FormLabel>
                    <Input
                      type="email"
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      placeholder="you@company.com"
                      size="lg"
                      borderWidth="2px"
                      borderColor="gray.200"
                      borderRadius="lg"
                      bg="white"
                      color="gray.900"
                      _placeholder={{ color: "gray.400" }}
                      _focus={{
                        borderColor: "#1e3a5f",
                        boxShadow: "0 0 0 3px rgba(30, 58, 95, 0.1)",
                        bg: "white"
                      }}
                      _hover={{ borderColor: "gray.300" }}
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel fontSize="sm" fontWeight="600" color="gray.700" mb={2}>
                      Password
                    </FormLabel>
                    <InputGroup size="lg">
                      <Input
                        type={showLoginPassword ? "text" : "password"}
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        placeholder="Enter your password"
                        borderWidth="2px"
                        borderColor="gray.200"
                        borderRadius="lg"
                        bg="white"
                        color="gray.900"
                        _placeholder={{ color: "gray.400" }}
                        _focus={{
                          borderColor: "#1e3a5f",
                          boxShadow: "0 0 0 3px rgba(30, 58, 95, 0.1)",
                          bg: "white"
                        }}
                        _hover={{ borderColor: "gray.300" }}
                        pr={12}
                      />
                      <InputRightElement>
                        <IconButton
                          h="full"
                          size="sm"
                          bg="transparent"
                          icon={showLoginPassword ? <ViewOffIcon color="gray.600" /> : <ViewIcon color="gray.600" />}
                          onClick={() => setShowLoginPassword(!showLoginPassword)}
                          _hover={{ bg: "gray.100" }}
                          aria-label={showLoginPassword ? "Hide password" : "Show password"}
                        />
                      </InputRightElement>
                    </InputGroup>
                  </FormControl>

                  <Box w="full" display="flex" justifyContent="space-between" alignItems="center">
                    <Checkbox
                      isChecked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      colorScheme="blue"
                    >
                      <Text fontSize="sm" color="gray.600">Remember me</Text>
                    </Checkbox>
                    <Text fontSize="xs" color="#0f172a" fontWeight="600" cursor="pointer" _hover={{ textDecoration: "underline" }}>
                      Forgot password?
                    </Text>
                  </Box>

                  <Button
                    w="full"
                    size="lg"
                    bg="linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)"
                    color="white"
                    fontWeight="700"
                    onClick={handleLogin}
                    isLoading={loading}
                    _hover={{
                      opacity: 0.9,
                      transform: "translateY(-2px)",
                      boxShadow: "0 10px 25px rgba(15, 23, 42, 0.2)"
                    }}
                    _active={{ transform: "translateY(0)" }}
                    transition="all 0.2s"
                  >
                    Sign In
                  </Button>
                </VStack>
              </TabPanel>

              {/* Register Tab */}
              <TabPanel>
                <VStack spacing={4}>
                  {/* Row 1: Full Name and Email */}
                  <Grid w="full" templateColumns="1fr 1fr" gap={4}>
                    <GridItem>
                      <FormControl isRequired>
                        <FormLabel fontSize="sm" fontWeight="600" color="gray.700" mb={2}>
                          Full Name
                        </FormLabel>
                        <Input
                          value={regFullName}
                          onChange={(e) => setRegFullName(e.target.value)}
                          placeholder="John Doe"
                          size="lg"
                          borderWidth="2px"
                          borderColor="gray.200"
                          borderRadius="lg"
                          bg="white"
                          color="gray.900"
                          _placeholder={{ color: "gray.400" }}
                          _focus={{
                            borderColor: "#1e3a5f",
                            boxShadow: "0 0 0 3px rgba(30, 58, 95, 0.1)",
                            bg: "white"
                          }}
                          _hover={{ borderColor: "gray.300" }}
                        />
                      </FormControl>
                    </GridItem>
                    <GridItem>
                      <FormControl isRequired>
                        <FormLabel fontSize="sm" fontWeight="600" color="gray.700" mb={2}>
                          Email Address
                        </FormLabel>
                        <Input
                          type="email"
                          value={regEmail}
                          onChange={(e) => setRegEmail(e.target.value)}
                          placeholder="you@company.com"
                          size="lg"
                          borderWidth="2px"
                          borderColor="gray.200"
                          borderRadius="lg"
                          bg="white"
                          color="gray.900"
                          _placeholder={{ color: "gray.400" }}
                          _focus={{
                            borderColor: "#1e3a5f",
                            boxShadow: "0 0 0 3px rgba(30, 58, 95, 0.1)",
                            bg: "white"
                          }}
                          _hover={{ borderColor: "gray.300" }}
                        />
                      </FormControl>
                    </GridItem>
                  </Grid>

                  {/* Row 2: Role and Department */}
                  <Grid w="full" templateColumns="1fr 1fr" gap={4}>
                    <GridItem>
                      <FormControl isRequired>
                        <FormLabel fontSize="sm" fontWeight="600" color="gray.700" mb={2}>
                          Role
                        </FormLabel>
                        <Select
                          value={regRole}
                          onChange={(e) => setRegRole(e.target.value)}
                          size="lg"
                          borderWidth="2px"
                          borderColor="gray.200"
                          borderRadius="lg"
                          bg="white"
                          color="gray.900"
                          _focus={{
                            borderColor: "#1e3a5f",
                            boxShadow: "0 0 0 3px rgba(30, 58, 95, 0.1)"
                          }}
                          _hover={{ borderColor: "gray.300" }}
                          sx={{
                            "& option": {
                              bg: "white",
                              color: "gray.900",
                            },
                            "& option:checked": {
                              bg: "#1e3a5f",
                              color: "white",
                            },
                          }}
                        >
                          {ROLES.map((role) => (
                            <option key={role} value={role}>
                              {role}
                            </option>
                          ))}
                        </Select>
                      </FormControl>
                    </GridItem>
                    <GridItem>
                      {regRole !== "C-Level" ? (
                        <FormControl isRequired>
                          <FormLabel fontSize="sm" fontWeight="600" color="gray.700" mb={2}>
                            Department
                          </FormLabel>
                          <Select
                            value={regDepartment}
                            onChange={(e) => setRegDepartment(e.target.value)}
                            size="lg"
                            borderWidth="2px"
                            borderColor="gray.200"
                            borderRadius="lg"
                            bg="white"
                            color="gray.900"
                            _focus={{
                              borderColor: "#1e3a5f",
                              boxShadow: "0 0 0 3px rgba(30, 58, 95, 0.1)"
                            }}
                            _hover={{ borderColor: "gray.300" }}
                            sx={{
                              "& option": {
                                bg: "white",
                                color: "gray.900",
                              },
                              "& option:checked": {
                                bg: "#1e3a5f",
                                color: "white",
                              },
                            }}
                          >
                            {DEPARTMENTS.filter((d) => d !== "Administration").map((dept) => (
                              <option key={dept} value={dept}>
                                {dept}
                              </option>
                            ))}
                          </Select>
                        </FormControl>
                      ) : (
                        <Box />
                      )}
                    </GridItem>
                  </Grid>

                  {/* Row 3: Password and Confirm Password */}
                  <Grid w="full" templateColumns="1fr 1fr" gap={4}>
                    <GridItem>
                      <FormControl isRequired>
                        <FormLabel fontSize="sm" fontWeight="600" color="gray.700" mb={2}>
                          Password
                        </FormLabel>
                        <InputGroup size="lg">
                          <Input
                            type={showRegPassword ? "text" : "password"}
                            value={regPassword}
                            onChange={(e) => setRegPassword(e.target.value)}
                            placeholder="At least 8 characters"
                            borderWidth="2px"
                            borderColor="gray.200"
                            borderRadius="lg"
                            bg="white"
                            color="gray.900"
                            _placeholder={{ color: "gray.400" }}
                            _focus={{
                              borderColor: "#1e3a5f",
                              boxShadow: "0 0 0 3px rgba(30, 58, 95, 0.1)",
                              bg: "white"
                            }}
                            _hover={{ borderColor: "gray.300" }}
                            pr={12}
                          />
                          <InputRightElement>
                            <IconButton
                              h="full"
                              size="sm"
                              bg="transparent"
                              icon={showRegPassword ? <ViewOffIcon color="gray.600" /> : <ViewIcon color="gray.600" />}
                              onClick={() => setShowRegPassword(!showRegPassword)}
                              _hover={{ bg: "gray.100" }}
                              aria-label={showRegPassword ? "Hide password" : "Show password"}
                            />
                          </InputRightElement>
                        </InputGroup>
                      </FormControl>
                    </GridItem>
                    <GridItem>
                      <FormControl isRequired>
                        <FormLabel fontSize="sm" fontWeight="600" color="gray.700" mb={2}>
                          Confirm Password
                        </FormLabel>
                        <InputGroup size="lg">
                          <Input
                            type={showRegConfirmPassword ? "text" : "password"}
                            value={regConfirmPassword}
                            onChange={(e) => setRegConfirmPassword(e.target.value)}
                            placeholder="Confirm password"
                            borderWidth="2px"
                            borderColor="gray.200"
                            borderRadius="lg"
                            bg="white"
                            color="gray.900"
                            _placeholder={{ color: "gray.400" }}
                            _focus={{
                              borderColor: "#1e3a5f",
                              boxShadow: "0 0 0 3px rgba(30, 58, 95, 0.1)",
                              bg: "white"
                            }}
                            _hover={{ borderColor: "gray.300" }}
                            pr={12}
                          />
                          <InputRightElement>
                            <IconButton
                              h="full"
                              size="sm"
                              bg="transparent"
                              icon={showRegConfirmPassword ? <ViewOffIcon color="gray.600" /> : <ViewIcon color="gray.600" />}
                              onClick={() => setShowRegConfirmPassword(!showRegConfirmPassword)}
                              _hover={{ bg: "gray.100" }}
                              aria-label={showRegConfirmPassword ? "Hide password" : "Show password"}
                            />
                          </InputRightElement>
                        </InputGroup>
                      </FormControl>
                    </GridItem>
                  </Grid>

                  <Button
                    w="full"
                    size="lg"
                    bg="linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)"
                    color="white"
                    fontWeight="700"
                    onClick={handleRegister}
                    isLoading={loading}
                    _hover={{
                      opacity: 0.9,
                      transform: "translateY(-2px)",
                      boxShadow: "0 10px 25px rgba(15, 23, 42, 0.2)"
                    }}
                    _active={{ transform: "translateY(0)" }}
                    transition="all 0.2s"
                    mt={2}
                  >
                    Create Account
                  </Button>
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </Box>
      </Container>
    </Box>
  )
}
