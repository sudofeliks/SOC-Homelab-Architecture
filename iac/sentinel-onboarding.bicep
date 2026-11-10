param location string = 'centralus'

resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: 'law-cyberrange-prod-cus'
}

resource sentinel 'Microsoft.SecurityInsights/onboardingStates@2024-03-01' = {
  scope: law
  name: 'default'
  properties: {}
}