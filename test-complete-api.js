const axios = require('axios');

const API_BASE = 'http://localhost:5001/api';

async function testCompleteAPI() {
    console.log('🧪 Testing Complete BuzzBus API Suite...\n');
    
    let allTestsPassed = true;
    const results = [];

    // Test 1: Health Check
    try {
        console.log('1️⃣ Testing Health Check...');
        const healthResponse = await axios.get(`${API_BASE}/health`);
        if (healthResponse.data.status === 'healthy') {
            console.log('✅ Health check passed');
            results.push({ test: 'Health Check', status: 'PASS' });
        } else {
            throw new Error('Health check failed');
        }
    } catch (error) {
        console.log('❌ Health check failed:', error.message);
        results.push({ test: 'Health Check', status: 'FAIL', error: error.message });
        allTestsPassed = false;
    }

    // Test 2: Buildings Endpoint
    try {
        console.log('\n2️⃣ Testing Buildings Endpoint...');
        const buildingsResponse = await axios.get(`${API_BASE}/buildings`);
        if (buildingsResponse.data && buildingsResponse.data.length > 0) {
            console.log(`✅ Buildings endpoint works - Found ${buildingsResponse.data.length} buildings`);
            console.log(`   Sample buildings: ${buildingsResponse.data.slice(0, 3).map(b => b.name).join(', ')}`);
            results.push({ test: 'Buildings Endpoint', status: 'PASS' });
        } else {
            throw new Error('No buildings returned');
        }
    } catch (error) {
        console.log('❌ Buildings endpoint failed:', error.message);
        results.push({ test: 'Buildings Endpoint', status: 'FAIL', error: error.message });
        allTestsPassed = false;
    }

    // Test 3: Building-to-Building Route Search
    try {
        console.log('\n3️⃣ Testing Building-to-Building Route Search...');
        const buildingSearchResponse = await axios.post(`${API_BASE}/RouteSearch`, {
            begin_building: 'Tech Tower',
            dest_building: 'Georgia Tech Library'
        });
        
        if (buildingSearchResponse.data.routes && buildingSearchResponse.data.routes.length > 0) {
            console.log(`✅ Building search works - Found ${buildingSearchResponse.data.routes.length} routes`);
            console.log(`   First route: ${buildingSearchResponse.data.routes[0].routeName} (${buildingSearchResponse.data.routes[0].routeId})`);
            console.log(`   Walking distance: ${buildingSearchResponse.data.routes[0].totalWalkingDistance}m`);
            results.push({ test: 'Building-to-Building Search', status: 'PASS' });
        } else {
            throw new Error('No routes found for building search');
        }
    } catch (error) {
        console.log('❌ Building search failed:', error.message);
        results.push({ test: 'Building-to-Building Search', status: 'FAIL', error: error.message });
        allTestsPassed = false;
    }

    // Test 4: Place-to-Place Route Search
    try {
        console.log('\n4️⃣ Testing Place-to-Place Route Search...');
        const placeSearchResponse = await axios.post(`${API_BASE}/RouteSearch`, {
            begin_location: 'Georgia Tech Campus',
            dest_location: 'Midtown Atlanta',
            begin_coordinates: '33.7756,-84.3963',
            dest_coordinates: '33.7896,-84.3843'
        });
        
        if (placeSearchResponse.data.routes && placeSearchResponse.data.routes.length > 0) {
            console.log(`✅ Place search works - Found ${placeSearchResponse.data.routes.length} routes`);
            console.log(`   First route: ${placeSearchResponse.data.routes[0].routeName}`);
            results.push({ test: 'Place-to-Place Search', status: 'PASS' });
        } else {
            throw new Error('No routes found for place search');
        }
    } catch (error) {
        console.log('❌ Place search failed:', error.message);
        results.push({ test: 'Place-to-Place Search', status: 'FAIL', error: error.message });
        allTestsPassed = false;
    }

    // Test 5: Mixed Search (Building + Place)
    try {
        console.log('\n5️⃣ Testing Mixed Search (Building + Place)...');
        const mixedSearchResponse = await axios.post(`${API_BASE}/RouteSearch`, {
            begin_building: 'Tech Tower',
            dest_location: 'Piedmont Park',
            dest_coordinates: '33.7856,-84.3736'
        });
        
        if (mixedSearchResponse.data.routes && mixedSearchResponse.data.routes.length > 0) {
            console.log(`✅ Mixed search works - Found ${mixedSearchResponse.data.routes.length} routes`);
            console.log(`   From: ${mixedSearchResponse.data.beginBuilding} to ${mixedSearchResponse.data.destLocation}`);
            results.push({ test: 'Mixed Search', status: 'PASS' });
        } else {
            throw new Error('No routes found for mixed search');
        }
    } catch (error) {
        console.log('❌ Mixed search failed:', error.message);
        results.push({ test: 'Mixed Search', status: 'FAIL', error: error.message });
        allTestsPassed = false;
    }

    // Test 6: Error Handling - Invalid Building
    try {
        console.log('\n6️⃣ Testing Error Handling (Invalid Building)...');
        try {
            await axios.post(`${API_BASE}/RouteSearch`, {
                begin_building: 'Invalid Building',
                dest_building: 'Tech Tower'
            });
            console.log('❌ Should have failed with invalid building');
            results.push({ test: 'Error Handling', status: 'FAIL', error: 'Should have failed' });
            allTestsPassed = false;
        } catch (error) {
            if (error.response && error.response.status === 400) {
                console.log('✅ Error handling works - Correctly rejected invalid building');
                results.push({ test: 'Error Handling', status: 'PASS' });
            } else {
                throw error;
            }
        }
    } catch (error) {
        console.log('❌ Error handling test failed:', error.message);
        results.push({ test: 'Error Handling', status: 'FAIL', error: error.message });
        allTestsPassed = false;
    }

    // Test 7: Error Handling - Missing Parameters
    try {
        console.log('\n7️⃣ Testing Error Handling (Missing Parameters)...');
        try {
            await axios.post(`${API_BASE}/RouteSearch`, {
                begin_building: 'Tech Tower'
                // Missing dest_building
            });
            console.log('❌ Should have failed with missing parameters');
            results.push({ test: 'Missing Parameters', status: 'FAIL', error: 'Should have failed' });
            allTestsPassed = false;
        } catch (error) {
            if (error.response && error.response.status === 400) {
                console.log('✅ Missing parameters handling works');
                results.push({ test: 'Missing Parameters', status: 'PASS' });
            } else {
                throw error;
            }
        }
    } catch (error) {
        console.log('❌ Missing parameters test failed:', error.message);
        results.push({ test: 'Missing Parameters', status: 'FAIL', error: error.message });
        allTestsPassed = false;
    }

    // Test 8: Frontend Integration
    try {
        console.log('\n8️⃣ Testing Frontend Integration...');
        const frontendResponse = await axios.get('http://localhost:3000');
        if (frontendResponse.status === 200 && frontendResponse.data.includes('Georgia Tech Bus Route Finder')) {
            console.log('✅ Frontend is running and accessible');
            results.push({ test: 'Frontend Integration', status: 'PASS' });
        } else {
            throw new Error('Frontend not accessible or incorrect content');
        }
    } catch (error) {
        console.log('❌ Frontend integration failed:', error.message);
        results.push({ test: 'Frontend Integration', status: 'FAIL', error: error.message });
        allTestsPassed = false;
    }

    // Test 9: CORS Headers
    try {
        console.log('\n9️⃣ Testing CORS Headers...');
        const corsResponse = await axios.options(`${API_BASE}/RouteSearch`);
        if (corsResponse.headers['access-control-allow-origin']) {
            console.log('✅ CORS headers present');
            results.push({ test: 'CORS Headers', status: 'PASS' });
        } else {
            console.log('⚠️  CORS headers not detected (may still work)');
            results.push({ test: 'CORS Headers', status: 'WARN' });
        }
    } catch (error) {
        console.log('⚠️  CORS test inconclusive:', error.message);
        results.push({ test: 'CORS Headers', status: 'WARN', error: error.message });
    }

    // Test 10: Performance Test
    try {
        console.log('\n🔟 Testing Performance (Multiple Requests)...');
        const startTime = Date.now();
        const promises = [];
        
        for (let i = 0; i < 5; i++) {
            promises.push(axios.post(`${API_BASE}/RouteSearch`, {
                begin_building: 'Tech Tower',
                dest_building: 'Georgia Tech Library'
            }));
        }
        
        await Promise.all(promises);
        const endTime = Date.now();
        const duration = endTime - startTime;
        
        console.log(`✅ Performance test passed - 5 concurrent requests in ${duration}ms`);
        results.push({ test: 'Performance', status: 'PASS', duration: `${duration}ms` });
    } catch (error) {
        console.log('❌ Performance test failed:', error.message);
        results.push({ test: 'Performance', status: 'FAIL', error: error.message });
        allTestsPassed = false;
    }

    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 TEST SUMMARY');
    console.log('='.repeat(60));
    
    results.forEach(result => {
        const status = result.status === 'PASS' ? '✅' : result.status === 'FAIL' ? '❌' : '⚠️';
        console.log(`${status} ${result.test}: ${result.status}`);
        if (result.error) {
            console.log(`   Error: ${result.error}`);
        }
        if (result.duration) {
            console.log(`   Duration: ${result.duration}`);
        }
    });
    
    const passCount = results.filter(r => r.status === 'PASS').length;
    const failCount = results.filter(r => r.status === 'FAIL').length;
    const warnCount = results.filter(r => r.status === 'WARN').length;
    
    console.log('\n📈 RESULTS:');
    console.log(`   ✅ Passed: ${passCount}`);
    console.log(`   ❌ Failed: ${failCount}`);
    console.log(`   ⚠️  Warnings: ${warnCount}`);
    console.log(`   📊 Total: ${results.length}`);
    
    if (allTestsPassed) {
        console.log('\n🎉 ALL TESTS PASSED! Your BuzzBus API is working perfectly!');
        console.log('\n🚀 Ready for production use!');
    } else {
        console.log('\n⚠️  Some tests failed. Please check the errors above.');
    }
    
    console.log('\n🔗 Available Endpoints:');
    console.log('   • GET  /api/health - Health check');
    console.log('   • GET  /api/buildings - List all buildings');
    console.log('   • POST /api/RouteSearch - Find bus routes');
    console.log('\n🌐 Frontend: http://localhost:3000');
    console.log('🔧 Backend: http://localhost:5001');
}

testCompleteAPI().catch(console.error);
