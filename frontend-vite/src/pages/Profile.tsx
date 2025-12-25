import React, { useState } from "react"
import {
  Box,
  VStack,
  HStack,
  Button,
  Input,
  FormControl,
  FormLabel,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  Badge,
  Grid,
  Stat,
  StatLabel,
  StatNumber,
  Divider,
  useToast,
  useColorModeValue,
  InputGroup,
  InputRightElement,
  IconButton,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  useDisclosure,
} from "@chakra-ui/react"
import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons"
import { useAuth } from "../hooks/useAuth"
import { useNavigate } from "react-router-dom"

export default function Profile() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const toast = useToast()

  // State
  const [isEditMode, setIsEditMode] = useState(false)
  const [fullName, setFullName] = useState(user?.fullName || "")
  const [showPasswordForm, setShowPasswordForm] = useState(false)
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)

  // Colors
  const bgGradient = useColorModeValue(
    "linear-gradient(135deg, #f0f4f8 0%, #d9e8f5 100%)",
    "linear-gradient(135deg, #1a202c 0%, #2d3748 100%)"
  )
  const pageBg = useColorModeValue("gray.50", "gray.900")
  const cardBg = useColorModeValue("white", "gray.800")
  const headerTextColor = useColorModeValue("gray.800", "white")
  const secondaryText = useColorModeValue("gray.600", "gray.400")
  const borderColor = useColorModeValue("gray.200", "gray.600")
  const statBg = useColorModeValue("blue.50", "gray.700")

  const { isOpen: isLogoutOpen, onOpen: onLogoutOpen, onClose: onLogoutClose } = useDisclosure()
  const cancelRef = React.useRef<HTMLButtonElement>(null)

  const getRoleColor = (role: string) => {
    const colors: { [key: string]: string } = {
      Finance: "blue",
      Marketing: "purple",
      HR: "green",
      Engineering: "orange",
      Employee: "gray",
      "C-Level": "red",
    }
    return colors[role] || "gray"
  }

  const getDeptColor = (dept: string) => {
    const colors: { [key: string]: string } = {
      Finance: "blue",
      Marketing: "purple",
      HR: "green",
      Engineering: "orange",
      Administration: "teal",
      General: "gray",
    }
    return colors[dept] || "gray"
  }

  const handleUpdateProfile = async () => {
    if (!fullName.trim()) {
      toast({
        title: "Validation Error",
        description: "Full name cannot be empty",
        status: "warning",
        duration: 3000,
        isClosable: true,
      })
      return
    }

    setLoading(true)
    try {
      // Mock API call - replace with actual endpoint when available
      await new Promise((resolve) => setTimeout(resolve, 500))

      toast({
        title: "Success",
        description: "Profile updated successfully",
        status: "success",
        duration: 3000,
        isClosable: true,
      })

      setIsEditMode(false)
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to update profile",
        status: "error",
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleChangePassword = async () => {
    if (!currentPassword || !newPassword || !confirmPassword) {
      toast({
        title: "Validation Error",
        description: "All password fields are required",
        status: "warning",
        duration: 3000,
        isClosable: true,
      })
      return
    }

    if (newPassword !== confirmPassword) {
      toast({
        title: "Validation Error",
        description: "New passwords do not match",
        status: "warning",
        duration: 3000,
        isClosable: true,
      })
      return
    }

    if (newPassword.length < 8) {
      toast({
        title: "Validation Error",
        description: "Password must be at least 8 characters",
        status: "warning",
        duration: 3000,
        isClosable: true,
      })
      return
    }

    setLoading(true)
    try {
      // Mock API call - replace with actual endpoint when available
      await new Promise((resolve) => setTimeout(resolve, 500))

      toast({
        title: "Success",
        description: "Password changed successfully",
        status: "success",
        duration: 3000,
        isClosable: true,
      })

      setShowPasswordForm(false)
      setCurrentPassword("")
      setNewPassword("")
      setConfirmPassword("")
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to change password",
        status: "error",
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    onLogoutClose()
    logout()
    navigate("/login")
  }

  return (
    <Box w="full" minH="100vh" bg={pageBg} p={6} overflowY="auto">
      <VStack spacing={0} align="stretch" h="full">
        {/* Gradient Header Section */}
        <Box bg={bgGradient} py={8} px={6} mb={8} borderRadius="lg">
          <VStack spacing={2} align="start">
            <Heading as="h1" size="2xl" color={headerTextColor} mb={2}>
              👤 My Profile
            </Heading>
            <Text color={secondaryText}>
              Manage your account information and security settings
            </Text>
          </VStack>
        </Box>

        <VStack spacing={8} align="stretch" flex={1} overflowY="auto" pb={8}>
          {/* Profile Summary Cards */}
          <Grid templateColumns={{ base: "1fr", md: "repeat(4, 1fr)" }} gap={4}>
            <Card bg={statBg} borderRadius="lg">
              <CardBody>
                <Stat>
                  <StatLabel color={secondaryText}>Full Name</StatLabel>
                  <StatNumber color={headerTextColor} fontSize="lg" mt={2}>
                    {user?.fullName}
                  </StatNumber>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={statBg} borderRadius="lg">
              <CardBody>
                <Stat>
                  <StatLabel color={secondaryText}>Email</StatLabel>
                  <StatNumber color={headerTextColor} fontSize="sm" mt={2} wordBreak="break-word">
                    {user?.email}
                  </StatNumber>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={statBg} borderRadius="lg">
              <CardBody>
                <Stat>
                  <StatLabel color={secondaryText}>Role</StatLabel>
                  <Badge colorScheme={getRoleColor(user?.role || "")} fontSize="md" mt={2}>
                    {user?.role}
                  </Badge>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={statBg} borderRadius="lg">
              <CardBody>
                <Stat>
                  <StatLabel color={secondaryText}>Status</StatLabel>
                  <Badge colorScheme="green" fontSize="md" mt={2}>
                    ✓ {user?.status}
                  </Badge>
                </Stat>
              </CardBody>
            </Card>
          </Grid>

          {/* Account Details Card */}
          <Card bg={cardBg} borderRadius="lg" borderWidth="1px" borderColor={borderColor}>
            <CardHeader borderBottomWidth="1px" borderColor={borderColor} pb={4}>
              <HStack justify="space-between" w="full">
                <Heading size="md" color={headerTextColor}>
                  📋 Account Details
                </Heading>
                {!isEditMode && (
                  <Button size="sm" colorScheme="blue" variant="ghost" onClick={() => setIsEditMode(true)}>
                    Edit
                  </Button>
                )}
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={6} align="stretch">
                {/* Account Info Grid */}
                <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={6}>
                  {/* Full Name */}
                  <FormControl>
                    <FormLabel color={headerTextColor} fontWeight="600">
                      Full Name
                    </FormLabel>
                    <Input
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Your full name"
                      isDisabled={!isEditMode}
                      borderWidth="2px"
                      borderColor={borderColor}
                    />
                  </FormControl>

                  {/* Email (Read-only) */}
                  <FormControl>
                    <FormLabel color={headerTextColor} fontWeight="600">
                      Email Address
                    </FormLabel>
                    <Input
                      type="email"
                      value={user?.email || ""}
                      isDisabled={true}
                      borderWidth="2px"
                      borderColor={borderColor}
                    />
                    <Text fontSize="xs" color={secondaryText} mt={1}>
                      Contact admin to change email
                    </Text>
                  </FormControl>

                  {/* Department */}
                  <FormControl>
                    <FormLabel color={headerTextColor} fontWeight="600">
                      Department
                    </FormLabel>
                    <Input
                      value={user?.department || ""}
                      isDisabled={true}
                      borderWidth="2px"
                      borderColor={borderColor}
                    />
                    <Text fontSize="xs" color={secondaryText} mt={1}>
                      Read-only information
                    </Text>
                  </FormControl>

                  {/* Role */}
                  <FormControl>
                    <FormLabel color={headerTextColor} fontWeight="600">
                      Role
                    </FormLabel>
                    <Input
                      value={user?.role || ""}
                      isDisabled={true}
                      borderWidth="2px"
                      borderColor={borderColor}
                    />
                    <Text fontSize="xs" color={secondaryText} mt={1}>
                      Read-only information
                    </Text>
                  </FormControl>
                </Grid>

                <Divider />

                {/* Edit Actions */}
                {isEditMode && (
                  <HStack spacing={3} justify="flex-end">
                    <Button
                      variant="ghost"
                      onClick={() => {
                        setIsEditMode(false)
                        setFullName(user?.fullName || "")
                      }}
                      isDisabled={loading}
                    >
                      Cancel
                    </Button>
                    <Button
                      colorScheme="blue"
                      onClick={handleUpdateProfile}
                      isLoading={loading}
                    >
                      Save Changes
                    </Button>
                  </HStack>
                )}
              </VStack>
            </CardBody>
          </Card>

          {/* Security Card */}
          <Card bg={cardBg} borderRadius="lg" borderWidth="1px" borderColor={borderColor}>
            <CardHeader borderBottomWidth="1px" borderColor={borderColor} pb={4}>
              <HStack justify="space-between" w="full">
                <Heading size="md" color={headerTextColor}>
                  🔒 Security
                </Heading>
                {!showPasswordForm && (
                  <Button
                    size="sm"
                    colorScheme="orange"
                    variant="ghost"
                    onClick={() => setShowPasswordForm(true)}
                  >
                    Change Password
                  </Button>
                )}
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                {!showPasswordForm ? (
                  <VStack spacing={3} align="start">
                    <Text color={secondaryText}>
                      🔐 Keep your account secure by using a strong password
                    </Text>
                    <Text fontSize="sm" color={secondaryText}>
                      • Password must be at least 8 characters
                      <br />
                      • Use a mix of uppercase, lowercase, numbers and symbols
                      <br />
                      • Change your password regularly
                    </Text>
                  </VStack>
                ) : (
                  <VStack spacing={4} align="stretch">
                    {/* Current Password */}
                    <FormControl>
                      <FormLabel color={headerTextColor} fontWeight="600">
                        Current Password
                      </FormLabel>
                      <InputGroup>
                        <Input
                          type={showCurrentPassword ? "text" : "password"}
                          value={currentPassword}
                          onChange={(e) => setCurrentPassword(e.target.value)}
                          placeholder="Enter current password"
                          borderWidth="2px"
                          borderColor={borderColor}
                        />
                        <InputRightElement>
                          <IconButton
                            h="full"
                            size="sm"
                            bg="transparent"
                            icon={
                              showCurrentPassword ? (
                                <ViewOffIcon color="gray.600" />
                              ) : (
                                <ViewIcon color="gray.600" />
                              )
                            }
                            onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                            aria-label={showCurrentPassword ? "Hide password" : "Show password"}
                          />
                        </InputRightElement>
                      </InputGroup>
                    </FormControl>

                    {/* New Password */}
                    <FormControl>
                      <FormLabel color={headerTextColor} fontWeight="600">
                        New Password
                      </FormLabel>
                      <InputGroup>
                        <Input
                          type={showNewPassword ? "text" : "password"}
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          placeholder="Enter new password"
                          borderWidth="2px"
                          borderColor={borderColor}
                        />
                        <InputRightElement>
                          <IconButton
                            h="full"
                            size="sm"
                            bg="transparent"
                            icon={
                              showNewPassword ? (
                                <ViewOffIcon color="gray.600" />
                              ) : (
                                <ViewIcon color="gray.600" />
                              )
                            }
                            onClick={() => setShowNewPassword(!showNewPassword)}
                            aria-label={showNewPassword ? "Hide password" : "Show password"}
                          />
                        </InputRightElement>
                      </InputGroup>
                    </FormControl>

                    {/* Confirm Password */}
                    <FormControl>
                      <FormLabel color={headerTextColor} fontWeight="600">
                        Confirm New Password
                      </FormLabel>
                      <InputGroup>
                        <Input
                          type={showConfirmPassword ? "text" : "password"}
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          placeholder="Confirm new password"
                          borderWidth="2px"
                          borderColor={borderColor}
                        />
                        <InputRightElement>
                          <IconButton
                            h="full"
                            size="sm"
                            bg="transparent"
                            icon={
                              showConfirmPassword ? (
                                <ViewOffIcon color="gray.600" />
                              ) : (
                                <ViewIcon color="gray.600" />
                              )
                            }
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                          />
                        </InputRightElement>
                      </InputGroup>
                    </FormControl>

                    <Divider />

                    <HStack spacing={3} justify="flex-end">
                      <Button
                        variant="ghost"
                        onClick={() => {
                          setShowPasswordForm(false)
                          setCurrentPassword("")
                          setNewPassword("")
                          setConfirmPassword("")
                        }}
                        isDisabled={loading}
                      >
                        Cancel
                      </Button>
                      <Button
                        colorScheme="orange"
                        onClick={handleChangePassword}
                        isLoading={loading}
                      >
                        Change Password
                      </Button>
                    </HStack>
                  </VStack>
                )}
              </VStack>
            </CardBody>
          </Card>

          {/* Session Card */}
          <Card bg={cardBg} borderRadius="lg" borderWidth="1px" borderColor={borderColor}>
            <CardHeader borderBottomWidth="1px" borderColor={borderColor} pb={4}>
              <Heading size="md" color={headerTextColor}>
                🚀 Session
              </Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="start">
                <Text color={secondaryText}>
                  Logging out will end your current session and return you to the login page.
                </Text>
                <Button
                  colorScheme="red"
                  variant="outline"
                  onClick={onLogoutOpen}
                  w="full"
                >
                  Logout
                </Button>
              </VStack>
            </CardBody>
          </Card>
        </VStack>
      </VStack>

      {/* Logout Confirmation Dialog */}
      <AlertDialog isOpen={isLogoutOpen} leastDestructiveRef={cancelRef} onClose={onLogoutClose}>
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Logout
            </AlertDialogHeader>
            <AlertDialogBody>
              Are you sure you want to logout? You will need to login again to access the application.
            </AlertDialogBody>
            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onLogoutClose}>
                Cancel
              </Button>
              <Button colorScheme="red" onClick={handleLogout} ml={3}>
                Logout
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  )
}
