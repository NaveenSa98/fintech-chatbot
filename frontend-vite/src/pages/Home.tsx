"use client"

import {
  Box,
  Button,
  VStack,
  HStack,
  Grid,
  Text,
  useColorModeValue,
  Container,
  Badge,
  Flex,

} from "@chakra-ui/react"

import { useNavigate } from "react-router-dom"
import { useAuth } from "../hooks/useAuth"

export default function Home() {
  const navigate = useNavigate()
  const { user } = useAuth()


  const bgGradient = useColorModeValue(
    "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
    "linear-gradient(135deg, #1a202c 0%, #2d3748 100%)"
  )
  const cardBg = useColorModeValue("white", "gray.800")
  const textColor = useColorModeValue("gray.800", "white")
  const subTextColor = useColorModeValue("gray.600", "gray.300")
  const statBg = useColorModeValue("gray.50", "gray.700")
  const borderColor = useColorModeValue("gray.200", "gray.600")

  const StatCard = ({ icon, label, value, color }: { icon: string; label: string; value: string | React.ReactNode; color: string }) => (
    <Box
      bg={cardBg}
      p={6}
      borderRadius="xl"
      boxShadow="0 2px 8px rgba(0, 0, 0, 0.08)"
      border="1px"
      borderColor={borderColor}
      _hover={{ boxShadow: "0 8px 16px rgba(0, 0, 0, 0.12)", transform: "translateY(-2px)" }}
      transition="all 0.3s ease"
    >
      <VStack align="start" spacing={3}>
        <Box fontSize="2xl">{icon}</Box>
        <VStack align="start" spacing={1}>
          <Text fontSize="sm" fontWeight="600" color={subTextColor} textTransform="uppercase" letterSpacing="wide">
            {label}
          </Text>
          <Text fontSize="2xl" fontWeight="900" color={color}>
            {value}
          </Text>
        </VStack>
      </VStack>
    </Box>
  )

  const ActionCard = ({
    icon,
    title,
    description,
    action,
    onClick,
    gradient,
  }: {
    icon: string
    title: string
    description: string
    action: string
    onClick: () => void
    gradient: string
  }) => (
    <Box
      bg={cardBg}
      borderRadius="xl"
      overflow="hidden"
      boxShadow="0 2px 8px rgba(0, 0, 0, 0.08)"
      border="1px"
      borderColor={borderColor}
      _hover={{
        boxShadow: "0 12px 24px rgba(0, 0, 0, 0.15)",
        transform: "translateY(-4px)",
      }}
      transition="all 0.3s ease"
    >
      {/* Top Gradient Bar */}
      <Box h="3px" bg={gradient} />

      <VStack spacing={6} p={6} align="start">
        <Box fontSize="3xl">{icon}</Box>
        <VStack align="start" spacing={2} flex={1}>
          <Text fontSize="lg" fontWeight="700" color={textColor}>
            {title}
          </Text>
          <Text fontSize="sm" color={subTextColor} lineHeight="1.6">
            {description}
          </Text>
        </VStack>
        <Button
          w="full"
          bg={gradient}
          color="white"
          fontWeight="700"
          _hover={{ opacity: 0.9, transform: "scale(1.02)" }}
          _active={{ transform: "scale(0.98)" }}
          transition="all 0.2s"
          onClick={onClick}
        >
          {action}
        </Button>
      </VStack>
    </Box>
  )

  const FeatureItem = ({ icon, title, description }: { icon: string; title: string; description: string }) => (
    <HStack spacing={4} p={4} borderRadius="lg" bg={statBg} _hover={{ bg: useColorModeValue("gray.100", "gray.600") }} transition="all 0.2s">
      <Box fontSize="2xl" minW="fit-content">
        {icon}
      </Box>
      <VStack align="start" spacing={1}>
        <Text fontWeight="700" color={textColor}>
          {title}
        </Text>
        <Text fontSize="sm" color={subTextColor}>
          {description}
        </Text>
      </VStack>
    </HStack>
  )

  return (
    <Box display="flex" flexDirection="column" bg={useColorModeValue("gray.50", "gray.900")}>
      {/* Main Content Area with Sidebar */}
      <Flex flex={1} overflow="hidden">
       
        {/* Main Content */}
        <Box flex={1} display="flex" flexDirection="column" overflowY="auto">
          {/* Hero Section */}
          <Box bg={bgGradient} py={10} px={8} borderBottom="1px" borderColor={borderColor}>
            <Container maxW="1200px" centerContent>
              <VStack spacing={2} align="center" w="full">
                <Badge colorScheme="blue" variant="solid" px={4} py={2} fontSize="sm" fontWeight="700">
                  Welcome 
                </Badge>

                <Text fontSize={{ base: "2xl", md: "3xl" }} fontWeight="900" color={textColor} textAlign="center">
                  Hello, {user?.fullName} 👋
                </Text>
                <Text fontSize="md" color={subTextColor} textAlign="center" maxW="600px">
                  Your Enterprise AI Assistant for intelligent document management and analysis
                </Text>
              </VStack>
            </Container>
          </Box>

          {/* Main Content Area */}
          <Box flex={1} overflowY="auto" py={12} px={8}>
            <Container maxW="1200px">
              {/* User Profile Stats */}
              <VStack spacing={12} align="stretch">
                <VStack spacing={6}>
                  <VStack align="start" w="full" spacing={2}>
                    <Text fontSize="xl" fontWeight="900" color={textColor}>
                      Your Profile Overview
                    </Text>
                    <Text fontSize="sm" color={subTextColor}>
                      Quick access to your account information
                    </Text>
                  </VStack>

                  <Grid templateColumns={{ base: "1fr", md: "repeat(3, 1fr)" }} gap={6} w="full">
                    <StatCard icon="🎭" label="Role" value={user?.role} color="#1e3a5f" />
                    <StatCard icon="🏢" label="Department" value={user?.department} color="#0078d4" />
                    <StatCard icon="✅" label="Status" value="Active" color="#10b981" />
                  </Grid>
                </VStack>

                {/* Quick Actions */}
                <VStack spacing={6}>
                  <VStack align="start" w="full" spacing={2}>
                    <Text fontSize="xl" fontWeight="900" color={textColor}>
                      Quick Actions
                    </Text>
                    <Text fontSize="sm" color={subTextColor}>
                      Get started with your most common tasks
                    </Text>
                  </VStack>

                  <Grid templateColumns={{ base: "1fr", md: "repeat(3, 1fr)" }} gap={6} w="full">
                    <ActionCard
                      icon="💬"
                      title="AI Chat Assistant"
                      description="Ask questions about your department documents and get instant, accurate answers by chat assistant"
                      action="Start Chatting"
                      onClick={() => navigate("/chat")}
                      gradient="linear-gradient(135deg, #1e3a5f 0%, #0f172a 100% )"
                    />

                    <ActionCard
                      icon="📁"
                      title="Document Management"
                      description={
                        user?.role === "C-Level"
                          ? "Upload, organize, and manage company documents with ease"
                          : "Browse, search, and access department documents securely"
                      }
                      action="Manage Documents"
                      onClick={() => navigate("/documents")}
                      gradient="linear-gradient(135deg, #06b6d4 0%, #054b5dff 100%)"
                    />

                    <ActionCard
                      icon="👤"
                      title="Account Settings"
                      description="View and update your profile information, preferences, and security settings"
                      action="View Profile"
                      onClick={() => navigate("/profile")}
                      gradient="linear-gradient(135deg, #8b5cf6 0%, #440ba5ff 100%)"
                    />
                  </Grid>
                </VStack>

                {/* Platform Features */}
                <VStack spacing={6}>
                  <VStack align="start" w="full" spacing={2}>
                    <Text fontSize="xl" fontWeight="900" color={textColor}>
                      Platform Features
                    </Text>
                    <Text fontSize="sm" color={subTextColor}>
                      Discover what makes our AI assistant powerful
                    </Text>
                  </VStack>

                  <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={4} w="full">
                    <FeatureItem
                      icon="🤖"
                      title="RAG-Powered Intelligence"
                      description="Advanced AI that understands your documents and provides context-aware answers"
                    />
                    <FeatureItem
                      icon="📊"
                      title="Smart Analytics"
                      description="Gain insights from your documents with intelligent analysis and reporting"
                    />
                    <FeatureItem
                      icon="🔐"
                      title="Enterprise Security"
                      description="Role-based access control with end-to-end encryption for your data"
                    />
                    <FeatureItem
                      icon="⚡"
                      title="Lightning Fast"
                      description="Instant responses and seamless document processing at scale"
                    />
                    <FeatureItem
                      icon="🔄"
                      title="Conversation Memory"
                      description="AI remembers context from previous conversations for better continuity"
                    />
                    <FeatureItem
                      icon="🌐"
                      title="Multi-Department Support"
                      description="Organize and access documents across different departments securely"
                    />
                  </Grid>
                </VStack>

                {/* Footer CTA
                <Box bg={statBg} p={8} borderRadius="xl" border="1px" borderColor={borderColor} textAlign="center">
                  <VStack spacing={4}>
                    <VStack spacing={2}>
                      <Text fontSize="lg" fontWeight="700" color={textColor}>
                        Ready to get started?
                      </Text>
                      <Text color={subTextColor}>
                        Dive into the chat assistant or explore your documents to unlock the power of AI
                      </Text>
                    </VStack>
                    <HStack spacing={4} justify="center">
                      <Button
                        bg="linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)"
                        color="white"
                        fontWeight="700"
                        size="lg"
                        onClick={() => navigate("/chat")}
                        _hover={{ opacity: 0.9 }}
                      >
                        Start Chatting
                      </Button>
                      <Button
                        variant="outline"
                        borderColor={borderColor}
                        color={textColor}
                        fontWeight="700"
                        size="lg"
                        onClick={() => navigate("/documents")}
                        _hover={{ bg: statBg }}
                      >
                        Explore Documents
                      </Button>
                    </HStack>
                  </VStack>
                </Box> */}
              </VStack>
            </Container>
          </Box>
        </Box>
        </Flex>
      </Box>
  )
}
