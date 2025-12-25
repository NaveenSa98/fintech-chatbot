import React, { useState, useEffect } from "react"
import {
  Box,
  VStack,
  HStack,
  Button,
  Input,
  Select,
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
  Spinner,
  useToast,
  useColorModeValue,
  Flex,
  InputGroup,
  InputLeftElement,
  Tooltip,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  useDisclosure,
} from "@chakra-ui/react"
import { DeleteIcon, SearchIcon } from "@chakra-ui/icons"
import { useAuth } from "../hooks/useAuth"
import { documentAPI } from "../services/api"

interface Document {
  id: number
  filename: string
  original_filename: string
  file_size: number
  file_type: string
  department: string
  is_processed: boolean
  chunk_count: number
  uploaded_by: number
  description?: string
  uploaded_at: Date
  processed_at?: Date
}

const DEPARTMENTS = ["Finance", "Marketing", "HR", "Engineering", "General"]

export default function Documents() {
  const { user } = useAuth()
  const toast = useToast()

  // State
  const [documents, setDocuments] = useState<Document[]>([])
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedDept, setSelectedDept] = useState("")
  const [description, setDescription] = useState("")
  const [deleteDocId, setDeleteDocId] = useState<number | null>(null)

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
  const hoverBg = useColorModeValue("gray.50", "gray.700")
  const statBg = useColorModeValue("blue.50", "gray.700")

  const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure()
  const cancelRef = React.useRef<HTMLButtonElement>(null)

  // Check if user can upload (C-Level only)
  const canUpload = user?.role === "C-Level"

  // Load documents on mount
  useEffect(() => {
    loadDocuments()
  }, [])

  // Filter documents when search term changes
  useEffect(() => {
    const filtered = documents.filter(
      (doc) =>
        doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.original_filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.department.toLowerCase().includes(searchTerm.toLowerCase())
    )
    setFilteredDocuments(filtered)
  }, [searchTerm, documents])

  const loadDocuments = async () => {
    setLoading(true)
    try {
      const response = await documentAPI.listDocuments(100)
      const docsData = response.documents || []
      const mappedDocs: Document[] = docsData.map((doc: any) => ({
        id: doc.id,
        filename: doc.filename,
        original_filename: doc.original_filename,
        file_size: doc.file_size,
        file_type: doc.file_type,
        department: doc.department,
        is_processed: doc.is_processed,
        chunk_count: doc.chunk_count,
        uploaded_by: doc.uploaded_by,
        description: doc.description,
        uploaded_at: new Date(doc.uploaded_at),
        processed_at: doc.processed_at ? new Date(doc.processed_at) : undefined,
      }))
      setDocuments(mappedDocs)
    } catch (error: any) {
      toast({
        title: "Error loading documents",
        description: error.response?.data?.detail || "Failed to load documents",
        status: "error",
        duration: 4000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: "Maximum file size is 10MB",
        status: "error",
        duration: 3000,
        isClosable: true,
      })
      return
    }

    setSelectedFile(file)
  }

  const handleUpload = async () => {
    if (!selectedFile || !selectedDept) {
      toast({
        title: "Missing information",
        description: "Please select both a file and department",
        status: "warning",
        duration: 3000,
        isClosable: true,
      })
      return
    }

    setUploading(true)
    try {
      await documentAPI.uploadDocument(
        selectedFile,
        selectedFile.name,
        selectedDept,
        description || undefined
      )

      toast({
        title: "Success",
        description: "Document uploaded successfully! Processing started...",
        status: "success",
        duration: 4000,
        isClosable: true,
      })

      // Reset form
      setSelectedFile(null)
      setSelectedDept("")
      setDescription("")

      // Reload documents
      await loadDocuments()
    } catch (error: any) {
      toast({
        title: "Upload failed",
        description: error.response?.data?.detail || "Failed to upload document",
        status: "error",
        duration: 4000,
        isClosable: true,
      })
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteClick = (docId: number) => {
    setDeleteDocId(docId)
    onDeleteOpen()
  }

  const handleDeleteConfirm = async () => {
    if (!deleteDocId) return

    try {
      await documentAPI.deleteDocument(deleteDocId)
      setDocuments(documents.filter((d) => d.id !== deleteDocId))

      toast({
        title: "Success",
        description: "Document deleted successfully",
        status: "success",
        duration: 3000,
        isClosable: true,
      })
    } catch (error: any) {
      toast({
        title: "Delete failed",
        description: error.response?.data?.detail || "Failed to delete document",
        status: "error",
        duration: 4000,
        isClosable: true,
      })
    } finally {
      onDeleteClose()
      setDeleteDocId(null)
    }
  }

  // Calculate statistics
  const stats = {
    total: documents.length,
    processed: documents.filter((d) => d.is_processed).length,
    totalSize: documents.reduce((sum, d) => sum + d.file_size, 0),
    totalChunks: documents.reduce((sum, d) => sum + d.chunk_count, 0),
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 B"
    const k = 1024
    const sizes = ["B", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
  }

  const getDepartmentColor = (dept: string) => {
    const colors: { [key: string]: string } = {
      Finance: "blue",
      Marketing: "purple",
      HR: "green",
      Engineering: "orange",
      General: "gray",
    }
    return colors[dept] || "gray"
  }

  return (
    <Box w="full" minH="100vh" bg={pageBg} p={6} overflowY="auto">
      <VStack spacing={0} align="stretch" h="full">
        {/* Gradient Header Section */}
        <Box bg={bgGradient} py={8} px={6} mb={8} borderRadius="lg">
          <VStack spacing={2} align="start">
            <Heading as="h1" size="2xl" color={headerTextColor} mb={2}>
              📄 Document Management
            </Heading>
            <Text color={secondaryText}>
              Upload, manage, and organize your department documents
            </Text>
          </VStack>
        </Box>

        <VStack spacing={8} align="stretch" flex={1} overflowY="auto" pb={8}>

        {/* Statistics */}
        {documents.length > 0 && (
          <Grid templateColumns={{ base: "1fr", md: "repeat(4, 1fr)" }} gap={4}>
            <Card bg={statBg} borderRadius="lg">
              <CardBody>
                <Stat>
                  <StatLabel color={secondaryText}>Total Documents</StatLabel>
                  <StatNumber color={headerTextColor}>{stats.total}</StatNumber>
                </Stat>
              </CardBody>
            </Card>
            <Card bg={statBg} borderRadius="lg">
              <CardBody>
                <Stat>
                  <StatLabel color={secondaryText}>Processed</StatLabel>
                  <StatNumber color={headerTextColor}>{stats.processed}</StatNumber>
                </Stat>
              </CardBody>
            </Card>
            <Card bg={statBg} borderRadius="lg">
              <CardBody>
                <Stat>
                  <StatLabel color={secondaryText}>Total Size</StatLabel>
                  <StatNumber color={headerTextColor} fontSize="lg">
                    {formatFileSize(stats.totalSize)}
                  </StatNumber>
                </Stat>
              </CardBody>
            </Card>
            <Card bg={statBg} borderRadius="lg">
              <CardBody>
                <Stat>
                  <StatLabel color={secondaryText}>Total Chunks</StatLabel>
                  <StatNumber color={headerTextColor}>{stats.totalChunks}</StatNumber>
                </Stat>
              </CardBody>
            </Card>
          </Grid>
        )}

        {/* Upload Section */}
        {canUpload && (
          <Card bg={cardBg} borderRadius="lg" borderWidth="1px" borderColor={borderColor}>
            <CardHeader borderBottomWidth="1px" borderColor={borderColor} pb={4}>
              <Heading size="md" color={headerTextColor}>
                📤 Upload Document
              </Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={4}>
                <FormControl>
                  <FormLabel color={headerTextColor}>Select File</FormLabel>
                  <Input
                    type="file"
                    accept=".pdf,.docx,.md,.xlsx,.csv"
                    onChange={handleFileSelect}
                    cursor="pointer"
                    p={2}
                  />
                  {selectedFile && (
                    <Text fontSize="sm" color="green.500" mt={2}>
                      ✓ {selectedFile.name} ({formatFileSize(selectedFile.size)})
                    </Text>
                  )}
                  <Text fontSize="xs" color={secondaryText} mt={2}>
                    Supported formats: PDF, DOCX, Markdown (MD), Excel (XLSX), CSV
                  </Text>
                </FormControl>

                <FormControl>
                  <FormLabel color={headerTextColor}>Department</FormLabel>
                  <Select
                    value={selectedDept}
                    onChange={(e) => setSelectedDept(e.target.value)}
                    placeholder="Select department"
                  >
                    {DEPARTMENTS.map((dept) => (
                      <option key={dept} value={dept}>
                        {dept}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel color={headerTextColor}>Description (Optional)</FormLabel>
                  <Input
                    placeholder="Add a description for this document..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </FormControl>

                <Button
                  w="full"
                  colorScheme="blue"
                  onClick={handleUpload}
                  isLoading={uploading}
                  size="md"
                >
                  Upload Document
                </Button>
              </VStack>
            </CardBody>
          </Card>
        )}

        {/* Document List Section */}
        <Card bg={cardBg} borderRadius="lg" borderWidth="1px" borderColor={borderColor}>
          <CardHeader borderBottomWidth="1px" borderColor={borderColor} pb={4}>
            <Heading size="md" color={headerTextColor}>
              📚 Your Documents
            </Heading>
          </CardHeader>
          <CardBody>
            {loading ? (
              <VStack py={10} spacing={4}>
                <Spinner size="lg" color="blue.500" />
                <Text color={secondaryText}>Loading documents...</Text>
              </VStack>
            ) : documents.length === 0 ? (
              <VStack py={10} spacing={3}>
                <Box fontSize="4xl">📄</Box>
                <Text color={secondaryText} fontSize="lg" fontWeight="500">
                  No documents yet
                </Text>
                <Text color={secondaryText} fontSize="sm">
                  {canUpload ? "Upload your first document to get started" : "Waiting for admin to upload documents"}
                </Text>
              </VStack>
            ) : (
              <VStack spacing={4} align="stretch">
                {/* Search */}
                <InputGroup>
                  <InputLeftElement pointerEvents="none">
                    <SearchIcon color="gray.300" />
                  </InputLeftElement>
                  <Input
                    placeholder="Search documents..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    size="md"
                  />
                </InputGroup>

                {/* Document List */}
                {filteredDocuments.length === 0 ? (
                  <Text color={secondaryText} textAlign="center" py={4}>
                    No documents match your search
                  </Text>
                ) : (
                  <VStack spacing={3} align="stretch">
                    {filteredDocuments.map((doc) => (
                      <Box
                        key={doc.id}
                        p={4}
                        bg={hoverBg}
                        borderRadius="md"
                        borderWidth="1px"
                        borderColor={borderColor}
                        _hover={{ bg: useColorModeValue("gray.100", "gray.500") }}
                        transition="all 0.2s"
                      >
                        <Flex justify="space-between" align="start" gap={4}>
                          <Box flex={1}>
                            <HStack spacing={2} mb={2}>
                              <Heading size="sm" color={headerTextColor}>
                                {doc.original_filename}
                              </Heading>
                              <Badge
                                colorScheme={doc.is_processed ? "green" : "yellow"}
                                fontSize="xs"
                              >
                                {doc.is_processed ? "✓ Processed" : "Processing..."}
                              </Badge>
                            </HStack>

                            <HStack spacing={3} mb={2} flexWrap="wrap">
                              <Badge colorScheme={getDepartmentColor(doc.department)} variant="subtle">
                                {doc.department}
                              </Badge>
                              <Text fontSize="xs" color={secondaryText}>
                                {formatFileSize(doc.file_size)}
                              </Text>
                              <Text fontSize="xs" color={secondaryText}>
                                {doc.file_type.toUpperCase()}
                              </Text>
                              {doc.is_processed && (
                                <Text fontSize="xs" color={secondaryText}>
                                  {doc.chunk_count} chunks
                                </Text>
                              )}
                            </HStack>

                            <Text fontSize="xs" color={secondaryText}>
                              Uploaded {doc.uploaded_at.toLocaleDateString()} at{" "}
                              {doc.uploaded_at.toLocaleTimeString()}
                            </Text>
                            {doc.description && (
                              <Text fontSize="sm" color={secondaryText} mt={2} fontStyle="italic">
                                "{doc.description}"
                              </Text>
                            )}
                          </Box>

                          <HStack spacing={2}>
                            <Tooltip label="Delete document">
                              <Button
                                size="sm"
                                colorScheme="red"
                                variant="ghost"
                                onClick={() => handleDeleteClick(doc.id)}
                                isDisabled={uploading || loading}
                              >
                                <DeleteIcon />
                              </Button>
                            </Tooltip>
                          </HStack>
                        </Flex>
                      </Box>
                    ))}
                  </VStack>
                )}
              </VStack>
            )}
          </CardBody>
        </Card>

        {/* Delete Confirmation Dialog */}
        <AlertDialog isOpen={isDeleteOpen} leastDestructiveRef={cancelRef} onClose={onDeleteClose}>
          <AlertDialogOverlay>
            <AlertDialogContent>
              <AlertDialogHeader fontSize="lg" fontWeight="bold">
                Delete Document
              </AlertDialogHeader>
              <AlertDialogBody>
                Are you sure? This action cannot be undone and will remove the document from the vector store.
              </AlertDialogBody>
              <AlertDialogFooter>
                <Button ref={cancelRef} onClick={onDeleteClose}>
                  Cancel
                </Button>
                <Button colorScheme="red" onClick={handleDeleteConfirm} ml={3}>
                  Delete
                </Button>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialogOverlay>
        </AlertDialog>
        </VStack>
      </VStack>
    </Box>
  )
}
