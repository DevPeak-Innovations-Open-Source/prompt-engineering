<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <!-- Navigation -->
    <nav class="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-gray-200 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-2">
            <Icon name="i-heroicons-cube-transparent" class="w-8 h-8 text-blue-600" />
            <span class="text-xl font-bold text-gray-900">Mini N8N</span>
          </div>
          <div class="hidden md:flex items-center space-x-8">
            <a href="#features" class="text-gray-700 hover:text-blue-600 transition-colors">Features</a>
            <a href="#api" class="text-gray-700 hover:text-blue-600 transition-colors">API</a>
            <a href="#nodes" class="text-gray-700 hover:text-blue-600 transition-colors">Nodes</a>
            <a href="#getting-started" class="text-gray-700 hover:text-blue-600 transition-colors">Docs</a>
            <Button 
              @click="openApiDocs" 
              class="bg-blue-600 hover:bg-blue-700 text-white"
            >
              Try API
            </Button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-7xl mx-auto text-center">
        <div class="mb-8">
          <Badge class="bg-blue-100 text-blue-800 text-sm px-3 py-1">
            AI-Powered Workflow Automation
          </Badge>
        </div>
        <h1 class="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          Automate Workflows with
          <span class="text-blue-600">Intelligent Nodes</span>
        </h1>
        <p class="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          A powerful workflow automation system with AI-powered generation, modular nodes, 
          and seamless integration. Build, execute, and scale your automation workflows with ease.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
          <Button @click="openApiDocs" size="lg" class="bg-blue-600 hover:bg-blue-700">
            <Icon name="i-heroicons-play" class="w-5 h-5 mr-2" />
            Try Live API
          </Button>
          <Button @click="scrollToSection('getting-started')" size="lg" variant="outline">
            <Icon name="i-heroicons-book-open" class="w-5 h-5 mr-2" />
            View Documentation
          </Button>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20 px-4 sm:px-6 lg:px-8 bg-white">
      <div class="max-w-7xl mx-auto">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Powerful Features for Modern Automation
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Everything you need to build sophisticated workflow automations with AI assistance
          </p>
        </div>
        
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Card v-for="feature in features" :key="feature.title" class="p-6 hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <Icon :name="feature.icon" class="w-6 h-6 text-blue-600" />
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ feature.title }}</h3>
            <p class="text-gray-600">{{ feature.description }}</p>
          </Card>
        </div>
      </div>
    </section>

    <!-- API Section -->
    <section id="api" class="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div class="max-w-7xl mx-auto">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            RESTful API Endpoints
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Complete CRUD operations for workflows, execution management, and AI-powered generation
          </p>
        </div>
        
        <div class="text-center mt-12">
          <Button @click="openApiDocs" size="lg" class="bg-blue-600 hover:bg-blue-700">
            <Icon name="i-heroicons-arrow-top-right-on-square" class="w-5 h-5 mr-2" />
            Open Interactive API Docs
          </Button>
        </div>
      </div>
    </section>

    <!-- Nodes Section -->
    <section id="nodes" class="py-20 px-4 sm:px-6 lg:px-8 bg-white">
      <div class="max-w-7xl mx-auto">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Modular Node System
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Extensible nodes for every automation need with error handling and retries
          </p>
        </div>
        
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card v-for="node in nodes" :key="node.name" class="p-6 hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <Icon :name="node.icon" class="w-6 h-6 text-green-600" />
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ node.name }}</h3>
            <p class="text-gray-600 text-sm">{{ node.description }}</p>
          </Card>
        </div>
      </div>
    </section>

    <!-- Getting Started -->
    <section id="getting-started" class="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div class="max-w-7xl mx-auto">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Quick Start Guide
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Get up and running in minutes with our simple setup process
          </p>
        </div>
        
        <div class="grid md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl font-bold text-blue-600">1</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Start Backend</h3>
            <p class="text-gray-600">Run the FastAPI backend with Docker or locally</p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl font-bold text-blue-600">2</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Create Workflow</h3>
            <p class="text-gray-600">Use the API to create workflows manually or with AI</p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl font-bold text-blue-600">3</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Execute & Monitor</h3>
            <p class="text-gray-600">Run workflows and monitor execution in real-time</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-7xl mx-auto">
        <div class="grid md:grid-cols-4 gap-8">
          <div>
            <div class="flex items-center space-x-2 mb-4">
              <Icon name="i-heroicons-cube-transparent" class="w-6 h-6 text-blue-400" />
              <span class="text-lg font-bold">Mini N8N</span>
            </div>
            <p class="text-gray-400 text-sm">
              AI-powered workflow automation system for modern applications.
            </p>
          </div>
          <div>
            <h4 class="font-semibold mb-4">Product</h4>
            <ul class="space-y-2 text-gray-400 text-sm">
              <li><a href="#features" class="hover:text-white">Features</a></li>
              <li><a href="#api" class="hover:text-white">API Documentation</a></li>
              <li><a href="#nodes" class="hover:text-white">Node Types</a></li>
            </ul>
          </div>
          <div>
            <h4 class="font-semibold mb-4">Resources</h4>
            <ul class="space-y-2 text-gray-400 text-sm">
              <li><a href="#" class="hover:text-white">GitHub</a></li>
              <li><a href="#" class="hover:text-white">Examples</a></li>
              <li><a href="#" class="hover:text-white">Support</a></li>
            </ul>
          </div>
          <div>
            <h4 class="font-semibold mb-4">Connect</h4>
            <div class="flex space-x-4">
              <Button variant="ghost" size="sm" class="text-gray-400 hover:text-white">
                <Icon name="i-heroicons-globe-alt" class="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="sm" class="text-gray-400 hover:text-white">
                <Icon name="i-heroicons-document-text" class="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
        <div class="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400 text-sm">
          <p>Inspired by n8n.io • Built with FastAPI & Nuxt.js</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// API Status
const apiStatus = ref('Checking...')
const mobileMenuOpen = ref(false)

// Features data
const features = ref([
  {
    title: 'AI-Powered Generation',
    description: 'Generate complete workflows from natural language descriptions using advanced LLM technology',
    icon: 'i-heroicons-sparkles'
  },
  {
    title: 'Modular Node System',
    description: 'Extensible architecture with 5 built-in node types for HTTP, delays, conditions, Python code, and LLM interactions',
    icon: 'i-heroicons-cube'
  },
  {
    title: 'Async Execution Engine',
    description: 'High-performance asynchronous workflow execution with proper error handling and retry mechanisms',
    icon: 'i-heroicons-bolt'
  },
  {
    title: 'RESTful API',
    description: 'Complete REST API with CRUD operations, execution management, and real-time monitoring',
    icon: 'i-heroicons-server-stack'
  },
  {
    title: 'Persistent Storage',
    description: 'SQLite database with async SQLAlchemy for workflow storage and execution logs',
    icon: 'i-heroicons-database'
  },
  {
    title: 'Production Ready',
    description: 'Docker containerization, comprehensive testing, and enterprise-grade error handling',
    icon: 'i-heroicons-shield-check'
  }
])

// Node types data
const nodes = ref([
  {
    name: 'HTTP Request',
    description: 'Make REST API calls with full HTTP method support, headers, and variable interpolation',
    icon: 'i-heroicons-globe-alt'
  },
  {
    name: 'Delay',
    description: 'Add configurable delays between workflow steps with async sleep functionality',
    icon: 'i-heroicons-clock'
  },
  {
    name: 'Condition',
    description: 'Conditional branching with 8 comparison operators for complex decision logic',
    icon: 'i-heroicons-fork'
  },
  {
    name: 'Python Code',
    description: 'Execute custom Python code in a sandboxed environment with timeout protection',
    icon: 'i-heroicons-code-bracket'
  },
  {
    name: 'LLM',
    description: 'Interact with language models for AI-powered text generation and analysis',
    icon: 'i-heroicons-chat-bubble-left-right'
  }
])

// Workflow API endpoints
const workflowEndpoints = ref([
  {
    method: 'POST',
    path: '/api/v1/workflows/',
    description: 'Create a new workflow with validation'
  },
  {
    method: 'GET',
    path: '/api/v1/workflows/',
    description: 'List all workflows with pagination'
  },
  {
    method: 'GET',
    path: '/api/v1/workflows/{id}',
    description: 'Get a specific workflow by ID'
  },
  {
    method: 'PUT',
    path: '/api/v1/workflows/{id}',
    description: 'Update an existing workflow'
  },
  {
    method: 'DELETE',
    path: '/api/v1/workflows/{id}',
    description: 'Delete a workflow'
  }
])

// Execution API endpoints
const executionEndpoints = ref([
  {
    method: 'POST',
    path: '/api/v1/workflows/execute',
    description: 'Execute a workflow with input data'
  },
  {
    method: 'POST',
    path: '/api/v1/workflows/generate',
    description: 'Generate workflow using AI from description'
  },
  {
    method: 'GET',
    path: '/api/v1/workflows/{id}/executions',
    description: 'List execution history for a workflow'
  },
  {
    method: 'GET',
    path: '/api/v1/workflows/executions/{id}',
    description: 'Get specific execution details'
  }
])

// Methods
const openApiDocs = () => {
  window.open('http://localhost:8000/docs', '_blank')
}

const scrollToSection = (sectionId) => {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const checkApiStatus = async () => {
  try {
    const response = await fetch('http://localhost:8000/health')
    if (response.ok) {
      apiStatus.value = 'Online'
    } else {
      apiStatus.value = 'Offline'
    }
  } catch (error) {
    apiStatus.value = 'Offline'
  }
}

// Check API status on mount
onMounted(() => {
  checkApiStatus()
  // Check status every 30 seconds
  setInterval(checkApiStatus, 30000)
})
</script>
