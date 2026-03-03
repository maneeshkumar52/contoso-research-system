// Azure Bicep template for Contoso Research System
// Deploy: az deployment group create --resource-group rg-research --template-file azure-deploy.bicep

@description('Location for all resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
param environmentName string = 'dev'

var prefix = 'contoso-research-${environmentName}'

resource openaiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: '${prefix}-openai'
  location: location
  kind: 'OpenAI'
  sku: { name: 'S0' }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-02-15-preview' = {
  name: '${prefix}-cosmos'
  location: location
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [{ locationName: location }]
    capabilities: [{ name: 'EnableServerless' }]
  }
}

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: '${prefix}-sb'
  location: location
  sku: { name: 'Standard', tier: 'Standard' }
}

output openaiEndpoint string = openaiAccount.properties.endpoint
output cosmosEndpoint string = cosmosAccount.properties.documentEndpoint
