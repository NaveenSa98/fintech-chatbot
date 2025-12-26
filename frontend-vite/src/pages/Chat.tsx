"use client"

import { VStack, Box, Flex, Input, Button, Checkbox, Text, useToast, Spinner, useColorModeValue, Container, HStack } from "@chakra-ui/react"
import { useState } from "react"
import type { Message } from "../types"
import { chatAPI } from "../services/api"

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [includeSources, setIncludeSources] = useState(true)
  const [loading, setLoading] = useState(false)
  const toast = useToast()

  // Theme colors
  const bgGradient = useColorModeValue(
    "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
    "linear-gradient(135deg, #1a202c 0%, #2d3748 100%)"
  )
  const contentBg = useColorModeValue("white", "gray.800")
  const textColor = useColorModeValue("gray.800", "white")
  const mutedText = useColorModeValue("gray.600", "gray.400")
  const messageBg = useColorModeValue("gray.50", "gray.700")
  const userMsgBg = useColorModeValue("blue.500", "blue.600")
  const assistantMsgBg = useColorModeValue("gray.100", "gray.700")
  const borderColor = useColorModeValue("gray.200", "gray.600")

  const handleSendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages([...messages, userMessage])
    setInput("")
    setLoading(true)

    try {
      const response = await chatAPI.sendMessage(input, undefined, includeSources)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.message,
        timestamp: new Date(response.timestamp),
        sources: response.sources || [],
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || "Failed to send message"
      toast({
        title: "Error",
        description: errorMessage,
        status: "error",
        duration: 3000,
      })
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Flex flexDirection="column" w="full" h="full" bg={useColorModeValue("gray.50", "gray.900")}>
      {/* Header Section */}
      <Box bg={bgGradient} py={6} px={8} borderBottom="1px" borderColor={borderColor}>
        <Container maxW="1000px" centerContent>
          <VStack spacing={2} align="center" w="full">
            <Text fontSize="2xl" fontWeight="900" color={textColor} textAlign="center">
              💬 AI Chat Assistant
            </Text>
            <Text fontSize="sm" color={mutedText} textAlign="center">
              Ask questions about your documents and get instant answers
            </Text>
          </VStack>
        </Container>
      </Box>

      {/* Chat Area */}
      <VStack flex={1} spacing={0} overflowY="auto" p={8} align="stretch">
        <Container maxW="1000px">
          <VStack spacing={4} align="stretch" pb={6}>
            {messages.length === 0 ? (
              <Box textAlign="center" py={20}>
                <Text fontSize="4xl" mb={4}>
                  💭
                </Text>
                <Text fontSize="xl" fontWeight="700" color={textColor} mb={2}>
                  Start a Conversation
                </Text>
                <Text fontSize="md" color={mutedText} maxW="400px" mx="auto">
                  Ask questions about your uploaded documents and get intelligent answers powered by AI
                </Text>
              </Box>
            ) : (
              messages.map((msg) => (
                <Flex key={msg.id} justify={msg.role === "user" ? "flex-end" : "flex-start"} w="full">
                  <Box
                    maxW="70%"
                    p={4}
                    borderRadius="xl"
                    bg={msg.role === "user" ? userMsgBg : assistantMsgBg}
                    color={msg.role === "user" ? "white" : textColor}
                    boxShadow="0 2px 8px rgba(0, 0, 0, 0.1)"
                  >
                    <Text whiteSpace="pre-wrap" lineHeight="1.6">
                      {msg.content}
                    </Text>

                    {msg.sources && msg.sources.length > 0 && (
                      <Box mt={3} pt={3} borderTop="1px" borderColor="currentColor" opacity={0.8}>
                        <Text fontSize="xs" fontWeight="bold" mb={2}>
                          📚 Sources:
                        </Text>
                        <VStack align="start" spacing={1}>
                          {(() => {
                            // Group sources by document name
                            const groupedSources = msg.sources.reduce((acc: any, source: any) => {
                              const docName = source.document_name || source.filename || "Unknown"
                              if (!acc[docName]) {
                                acc[docName] = {
                                  name: docName,
                                  count: 0,
                                  maxScore: 0,
                                  department: source.department || "Unknown",
                                }
                              }
                              acc[docName].count += 1
                              acc[docName].maxScore = Math.max(acc[docName].maxScore, source.relevance_score || 0)
                              return acc
                            }, {})

                            // Convert to array and sort by relevance
                            const uniqueSources = Object.values(groupedSources).sort(
                              (a: any, b: any) => b.maxScore - a.maxScore
                            )

                            return uniqueSources.map((source: any, idx: number) => (
                              <HStack key={idx} spacing={2} fontSize="xs" opacity={0.9} w="full">
                                <Text>
                                  • {source.name}
                                </Text>
                                {source.count > 1 && (
                                  <Text color="blue.300" fontWeight="bold">
                                    ({source.count} chunks)
                                  </Text>
                                )}
                                <Text color="gray.400" ml="auto">
                                  {Math.round(source.maxScore * 100)}% relevant
                                </Text>
                              </HStack>
                            ))
                          })()}
                        </VStack>
                      </Box>
                    )}

                    <Text fontSize="xs" mt={2} opacity={0.7}>
                      {msg.timestamp.toLocaleTimeString()}
                    </Text>
                  </Box>
                </Flex>
              ))
            )}

            {loading && (
              <Flex justify="flex-start">
                <HStack spacing={2} p={4} bg={assistantMsgBg} borderRadius="xl" color={textColor}>
                  <Spinner size="sm" />
                  <Text fontSize="sm" fontWeight="500">
                    Thinking...
                  </Text>
                </HStack>
              </Flex>
            )}
          </VStack>
        </Container>
      </VStack>

      {/* Input Section */}
      <Box bg={contentBg} borderTop="1px" borderColor={borderColor} p={6} mt="auto">
        <Container maxW="1000px">
          <VStack spacing={3} align="stretch">
            <HStack spacing={2} w="full">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !loading && handleSendMessage()}
                placeholder="Type your question here..."
                isDisabled={loading}
                size="lg"
                borderRadius="lg"
                bg={messageBg}
                color={textColor}
                _placeholder={{ color: mutedText }}
              />
              <Button colorScheme="blue" onClick={handleSendMessage} isLoading={loading} size="lg">
                Send
              </Button>
            </HStack>

            <HStack spacing={2} justify="space-between" fontSize="sm">
              <Checkbox isChecked={includeSources} onChange={(e) => setIncludeSources(e.target.checked)} color={textColor}>
                <Text color={textColor}>Include document sources</Text>
              </Checkbox>
              <Text color={mutedText}>{messages.filter((m) => m.role === "user").length} questions asked</Text>
            </HStack>
          </VStack>
        </Container>
      </Box>
    </Flex>
  )
}
