import api from './index.js'

export const getPlatforms = () => api.get('/company-intel/platforms')
export const generateAliases = (companyName) => api.post('/company-intel/aliases/generate', { company_name: companyName })
export const searchCompanyIntel = (data) => api.post('/company-intel/search', data)
export const getCompanyIntelQueries = () => api.get('/company-intel/queries')
export const getCompanyIntelQuery = (queryId) => api.get(`/company-intel/queries/${queryId}`)
export const getCompanyIntelJobs = (queryId) => api.get(`/company-intel/queries/${queryId}/jobs`)
export const getCompanyIntelQueryScore = (queryId) => api.get(`/company-intel/queries/${queryId}/score`)
export const getCompanyIntelCompanies = () => api.get('/company-intel/companies')
export const getCompanyIntelCompany = (companyId) => api.get(`/company-intel/companies/${companyId}`)
export const getCompanyIntelCompanyScore = (companyId) => api.get(`/company-intel/companies/${companyId}/score`)
export const getPlatformAccounts = () => api.get('/company-intel/platform-accounts')
export const openPlatformLogin = (platform) => api.post(`/company-intel/platform-accounts/${platform}/open-login`)
export const checkPlatformLogin = (platform) => api.post(`/company-intel/platform-accounts/${platform}/check`)
export const exportCompanyIntelQuery = (queryId) => {
  window.open(`/api/v1/company-intel/queries/${queryId}/export`, '_blank')
}
