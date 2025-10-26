#!/usr/bin/env node

const axios = require('axios');

const API_BASE_URL = 'http://localhost:5000';

async function testApi() {
    console.log('Testing BuzzBus .NET API...\n');

    try {
        // Test health endpoint
        console.log('1. Testing health endpoint...');
        const healthResponse = await axios.get(`${API_BASE_URL}/api/health`);
        console.log('✅ Health check passed:', healthResponse.data);
        console.log('');

        // Test buildings endpoint
        console.log('2. Testing buildings endpoint...');
        const buildingsResponse = await axios.get(`${API_BASE_URL}/api/buildings`);
        console.log('✅ Buildings endpoint passed. Found', buildingsResponse.data.length, 'buildings');
        console.log('Buildings:', buildingsResponse.data.slice(0, 3).join(', '), '...');
        console.log('');

        // Test route search endpoint
        console.log('3. Testing route search endpoint...');
        const searchResponse = await axios.post(`${API_BASE_URL}/api/route-search`, {
            begin_building: 'Tech Tower',
            dest_building: 'Student Center'
        });
        console.log('✅ Route search endpoint passed');
        console.log('Found', searchResponse.data.routes.length, 'routes');
        if (searchResponse.data.routes.length > 0) {
            const firstRoute = searchResponse.data.routes[0];
            console.log('First route:', firstRoute.route_name, '(ID:', firstRoute.route_id + ')');
        }
        console.log('');

        console.log('🎉 All API tests passed! The .NET backend is working correctly.');

    } catch (error) {
        console.error('❌ API test failed:');
        if (error.response) {
            console.error('Status:', error.response.status);
            console.error('Data:', error.response.data);
        } else if (error.request) {
            console.error('No response received. Is the API running on port 5000?');
        } else {
            console.error('Error:', error.message);
        }
        process.exit(1);
    }
}

testApi();
