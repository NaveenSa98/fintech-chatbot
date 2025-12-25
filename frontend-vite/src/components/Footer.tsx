"use client"

import { Box, Container, HStack, Text, useColorModeValue } from "@chakra-ui/react"

export default function Footer() {
  const footerBg = useColorModeValue("white", "gray.900")
  const footerBorderColor = useColorModeValue("gray.200", "gray.700")
  const textColor = useColorModeValue("gray.600", "gray.400")

  const currentYear = new Date().getFullYear()

  return (
    <Box
      bg={footerBg}
      borderTop="1px"
      borderColor={footerBorderColor}
      py={6}
      px={6}
      mt="auto"
    >
      <Container maxW="1200px">
        <HStack justify="center" spacing={2}>
          <Text fontSize="sm" color={textColor}>
            © {currentYear} FinTech Enterprise AI Assistant. All rights reserved.
          </Text>
        </HStack>
      </Container>
    </Box>
  )
}
