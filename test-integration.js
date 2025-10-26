#!/usr/bin/env node

const axios = require('axios');

async function testFullIntegration() {
    console.log('🧪 Testing BuzzBus Full Integration...\n');

    try {
        // Test 1: React app loads
        console.log('1. Testing React app...');
        const reactResponse = await axios.get('http://localhost:3000');
        if (reactResponse.data.includes('Georgia Tech Bus Route Finder')) {
            console.log('✅ React app loads successfully');
        } else {
            throw new Error('React app not loading properly');
        }

        // Test 2: Buildings API through React proxy
        console.log('\n2. Testing buildings API through React proxy...');
        const buildingsResponse = await axios.get('http://localhost:3000/api/buildings');
        if (buildingsResponse.data.length > 0) {
            console.log('✅ Buildings API works through React proxy');
            console.log(`   Found ${buildingsResponse.data.length} buildings`);
        } else {
            throw new Error('Buildings API not working');
        }

        // Test 3: Route search API through React proxy
        console.log('\n3. Testing route search API through React proxy...');
        const searchResponse = await axios.post('http://localhost:3000/api/RouteSearch', {
            begin_building: 'Tech Tower',
            dest_building: 'Student Center'
        });
        
        if (searchResponse.data.routes && searchResponse.data.routes.length > 0) {
            console.log('✅ Route search API works through React proxy');
            console.log(`   Found ${searchResponse.data.routes.length} routes`);
            console.log(`   First route: ${searchResponse.data.routes[0].routeName}`);
        } else {
            throw new Error('Route search API not working');
        }

        // Test 4: Direct .NET API (bypassing React proxy)
        console.log('\n4. Testing direct .NET API...');
        const directResponse = await axios.get('http://localhost:5001/api/health');
        if (directResponse.data.status === 'healthy') {
            console.log('✅ .NET API is healthy');
        } else {
            throw new Error('.NET API not healthy');
        }

        console.log('\n🎉 ALL TESTS PASSED! The integration actually works!');
        console.log('\n📱 You can now open http://localhost:3000 in your browser');
        console.log('   and use the full application with React frontend and .NET backend.');

    } catch (error) {
        console.error('\n❌ INTEGRATION TEST FAILED:');
        console.error(error.message);
        if (error.response) {
            console.error('Status:', error.response.status);
            console.error('Data:', error.response.data);
        }
        process.exit(1);
    }
}

testFullIntegration();
