"use client"

import { Box, VStack, Button, Text, Divider, HStack, useColorModeValue, Stat, StatLabel, StatNumber, IconButton, Spinner } from "@chakra-ui/react"
import { AddIcon, DeleteIcon, ArrowLeftIcon, ArrowRightIcon } from "@chakra-ui/icons"
import { useNavigate, useLocation } from "react-router-dom"
import { useState, useEffect } from "react"
import type { Conversation } from "../types"
import { chatAPI } from "../services/api"

interface SidebarProps {
  stats?: {
    totalMessages: number
    userQuestions: number
  }
}

export default function Sidebar({
  stats = { totalMessages: 0, userQuestions: 0 },
}: SidebarProps = {}) {
  const navigate = useNavigate()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [localConversations, setLocalConversations] = useState<Conversation[]>([])
  const [localSelectedConv, setLocalSelectedConv] = useState<string | null>(null)
  const [localLoading, setLocalLoading] = useState(false)

  const cardBg = useColorModeValue("white", "gray.800")
  const borderColor = useColorModeValue("gray.200", "gray.700")
  const textColor = useColorModeValue("gray.800", "white")
  const mutedText = useColorModeValue("gray.600", "gray.400")
  const hoverBg = useColorModeValue("gray.100", "gray.800")
  const activeBg = useColorModeValue("blue.50", "blue.900")
  const activeBorder = useColorModeValue("blue.400", "blue.300")

  const isActive = (path: string) => location.pathname === path
  const isChat = location.pathname === "/chat"

  // Load conversations when on chat page
  useEffect(() => {
    if (isChat) {
      loadConversations()
    }
  }, [isChat])

  const loadConversations = async () => {
    try {
      setLocalLoading(true)
      const response = await chatAPI.listConversations(10)
      if (response.conversations) {
        const formattedConversations = response.conversations.map((conv: any) => ({
          id: conv.id.toString(),
          title: conv.title,
          createdAt: new Date(conv.created_at),
          messages: [],
        }))
        setLocalConversations(formattedConversations)
      }
    } catch (error) {
      console.error("Failed to load conversations:", error)
    } finally {
      setLocalLoading(false)
    }
  }

  const handleNewConversation = () => {
    setLocalSelectedConv(null)
  }

  const handleSelectConversation = (id: string) => {
    setLocalSelectedConv(id)
  }

  const handleDeleteConversation = async (id: string) => {
    try {
      await chatAPI.deleteConversation(parseInt(id))
      setLocalConversations(localConversations.filter((c) => c.id !== id))
      if (localSelectedConv === id) {
        setLocalSelectedConv(null)
      }
    } catch (error) {
      console.error("Failed to delete conversation:", error)
    }
  }

  const NavButton = ({ icon, label, path }: { icon: string; label: string; path: string }) => (
    <Button
      w="full"
      justifyContent={sidebarOpen ? "start" : "center"}
      variant="ghost"
      onClick={() => navigate(path)}
      bg={isActive(path) ? activeBg : "transparent"}
      borderLeft={isActive(path) ? "4px" : "0px"}
      borderColor={isActive(path) ? activeBorder : "transparent"}
      color={isActive(path) ? "blue.600" : textColor}
      fontWeight={isActive(path) ? "700" : "500"}
      fontSize="sm"
      leftIcon={<Text fontSize="lg">{icon}</Text>}
      _hover={{ bg: hoverBg }}
      transition="all 0.2s"
      borderRadius="lg"
      pl={sidebarOpen ? 4 : 2}
      py={3}
      title={sidebarOpen ? undefined : label}
    >
      {sidebarOpen && label}
    </Button>
  )

  return (
    <Box
          w={sidebarOpen ? "280px" : "70px"}
          bg={cardBg}
          borderRight="1px"
          borderColor={borderColor}
          overflowY="auto"
          py={6}
          px={sidebarOpen ? 4 : 2}
          transition="all 0.3s ease"
          position="relative"
        >
      {/* Toggle Button */}
       <IconButton
                  aria-label="Toggle Sidebar"
                  icon={sidebarOpen ? <ArrowLeftIcon /> : <ArrowRightIcon />}
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  variant="ghost"
                  size="sm"
                  w="full"
                  mb={4}
                  _hover={{ bg: useColorModeValue("gray.100", "gray.700") }}
                />

      {/* Main Navigation */}
      <VStack spacing={1} align="stretch" mb={4}>
        {sidebarOpen && (
          <Text fontSize="xs" fontWeight="700" color={mutedText} textTransform="uppercase" letterSpacing="wider" px={2}>
            Main Menu
          </Text>
        )}
        <NavButton icon="🏠" label="Home" path="/" />
        <NavButton icon="💬" label="Chat" path="/chat" />
        <NavButton icon="📁" label="Documents" path="/documents" />
        <NavButton icon="👤" label="Profile" path="/profile" />
      </VStack>

      <Divider my={2} />

      {/* Chat Section - Only show on chat page */}
      {isChat && (
        <>
          <Button
            w="full"
            leftIcon={<AddIcon />}
            mb={3}
            colorScheme="blue"
            onClick={handleNewConversation}
            size="sm"
            justifyContent={sidebarOpen ? "start" : "center"}
          >
            {sidebarOpen ? "New Chat" : "+"}
          </Button>

          {sidebarOpen && (
            <Text fontSize="xs" fontWeight="700" color={mutedText} textTransform="uppercase" letterSpacing="wider" px={2} mb={2}>
              Chat History
            </Text>
          )}

          {localLoading ? (
            <VStack align="center" justify="center" py={4}>
              <Spinner size="sm" />
            </VStack>
          ) : (
            <VStack spacing={1} align="stretch" flex={1} overflow="hidden">
              {localConversations.length === 0 ? (
                <Text fontSize="sm" color={mutedText} p={2} textAlign="center">
                  {sidebarOpen ? "No chats yet" : "..."}
                </Text>
              ) : (
                <Box overflowY="auto" flex={1}>
                  <VStack spacing={1} align="stretch">
                    {localConversations.map((conv) => (
                      <HStack
                        key={conv.id}
                        p={2}
                        borderRadius="md"
                        cursor="pointer"
                        bg={localSelectedConv === conv.id ? activeBg : "transparent"}
                        borderLeft={localSelectedConv === conv.id ? "3px" : "0px"}
                        borderColor={localSelectedConv === conv.id ? activeBorder : "transparent"}
                        _hover={{ bg: hoverBg }}
                        transition="all 0.2s"
                        spacing={1}
                      >
                        <Box flex={1} onClick={() => handleSelectConversation(conv.id)} overflow="hidden" minW={0}>
                          {sidebarOpen && (
                            <>
                              <Text fontSize="sm" isTruncated color={textColor}>
                                {conv.title}
                              </Text>
                              <Text fontSize="xs" color={mutedText}>
                                {new Date(conv.createdAt).toLocaleDateString()}
                              </Text>
                            </>
                          )}
                        </Box>
                        {sidebarOpen && (
                          <Button
                            size="sm"
                            leftIcon={<DeleteIcon />}
                            variant="ghost"
                            onClick={() => handleDeleteConversation(conv.id)}
                            opacity={0.6}
                            _hover={{ opacity: 1 }}
                          />
                        )}
                      </HStack>
                    ))}
                  </VStack>
                </Box>
              )}
            </VStack>
          )}

          <Divider my={2} />

          {/* Statistics */}
          {sidebarOpen && (
            <VStack align="start" spacing={2} fontSize="sm">
              <Text fontWeight="700" color={textColor}>
                📊 Chat Stats
              </Text>
              <Stat size="sm">
                <StatLabel fontSize="xs" color={mutedText}>
                  Messages
                </StatLabel>
                <StatNumber fontSize="lg" color="blue.600">
                  {stats.totalMessages}
                </StatNumber>
              </Stat>
              <Stat size="sm">
                <StatLabel fontSize="xs" color={mutedText}>
                  Questions
                </StatLabel>
                <StatNumber fontSize="lg" color="green.600">
                  {stats.userQuestions}
                </StatNumber>
              </Stat>
            </VStack>
          )}
        </>
      )}
    </Box>
  )
}
