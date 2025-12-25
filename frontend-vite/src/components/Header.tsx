"use client"

import {
  Box,
  Flex,
  Button,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Avatar,
  HStack,
  Text,
  useColorMode,
  useColorModeValue,
  IconButton,
  Divider,
} from "@chakra-ui/react"
import { MoonIcon, SunIcon } from "@chakra-ui/icons"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../hooks/useAuth"

export default function Header() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const { colorMode, toggleColorMode } = useColorMode()

  const headerBg = useColorModeValue("white", "gray.900")
  const headerBorderColor = useColorModeValue("gray.200", "gray.700")
  const textColor = useColorModeValue("gray.800", "white")
  const headerLinkHoverBg = useColorModeValue("gray.100", "gray.800")

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  return (
    <Box
      bg={headerBg}
      boxShadow="0 4px 12px rgba(0, 0, 0, 0.08)"
      borderBottom="1px"
      borderColor={headerBorderColor}
      py={4}
      px={6}
      position="sticky"
      top={0}
      zIndex={100}
    >
      <Flex justify="space-between" align="center" w="full">
        {/* Left - Brand Logo & Title */}
        <Box cursor="pointer" onClick={() => navigate("/")} _hover={{ opacity: 0.85 }} transition="all 0.2s">
          <HStack spacing={2}>
            <Box fontSize="2xl" fontWeight="900" color="cyan.600">
              FinTech
            </Box>
            <Text fontSize="sm" fontWeight="700" color={textColor} display={{ base: "none", md: "block" }}>
              Enterprise AI
            </Text>
          </HStack>
        </Box>

        {/* Right Section - Theme Toggle & User Menu */}
        <HStack spacing={3}>
          <IconButton
            aria-label="Toggle color mode"
            icon={colorMode === "light" ? <MoonIcon /> : <SunIcon />}
            onClick={toggleColorMode}
            variant="ghost"
            _hover={{ bg: headerLinkHoverBg }}
            title={colorMode === "light" ? "Switch to dark mode" : "Switch to light mode"}
            size="lg"
          />

          <Menu>
            <MenuButton as={Button} rounded="full" cursor="pointer" minW={0} variant="unstyled" _hover={{ opacity: 0.8 }}>
              <Avatar
                name={user?.fullName}
                size="sm"
                bg="linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)"
                color="white"
                fontWeight="bold"
                fontSize="lg"
              />
            </MenuButton>
            <MenuList>
              {/* User Info Section */}
              <Box px={4} py={3}>
                <Text fontWeight="bold" fontSize="sm" color={textColor}>
                  {user?.fullName}
                </Text>
                <Text fontSize="xs" color="gray.500">
                  {user?.email}
                </Text>
                <Text fontSize="xs" color="gray.400" mt={1}>
                  {user?.role} • {user?.department}
                </Text>
              </Box>

              <Divider my={2} />

              <MenuItem onClick={() => navigate("/profile")} icon={<Text fontSize="lg">👤</Text>}>
                My Profile
              </MenuItem>

              <Divider my={2} />

              {/* Logout */}
              <MenuItem onClick={handleLogout} color="red.500" fontWeight="600" icon={<Text fontSize="lg">🚪</Text>}>
                Logout
              </MenuItem>
            </MenuList>
          </Menu>
        </HStack>
      </Flex>
    </Box>
  )
}
