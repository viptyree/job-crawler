import api from './index'

export const getDashboard = () => api.get('/stats/dashboard')
export const getSalaryTrend = (params) => api.get('/stats/salary-trend', { params })
export const getSkillHeatmap = (params) => api.get('/stats/skill-heatmap', { params })
export const getCityDistribution = (params) => api.get('/stats/city-distribution', { params })
export const getSettings = () => api.get('/settings')
export const updateSettings = (data) => api.put('/settings', data)
