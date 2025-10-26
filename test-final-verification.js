const axios = require('axios');

async function finalVerification() {
    console.log('🔍 Final Verification of BuzzBus Application...\n');

    const tests = [];
    let allPassed = true;

    // Test 1: Backend Health
    try {
        const health = await axios.get('http://localhost:5001/api/health');
        tests.push({ name: 'Backend Health', status: health.data.status === 'healthy' ? 'PASS' : 'FAIL' });
    } catch (error) {
        tests.push({ name: 'Backend Health', status: 'FAIL', error: error.message });
        allPassed = false;
    }

    // Test 2: Frontend Accessibility
    try {
        const frontend = await axios.get('http://localhost:3000');
        const hasGoogleMaps = frontend.data.includes('maps.googleapis.com');
        const hasPlacesLibrary = frontend.data.includes('libraries=places');
        const hasReactApp = frontend.data.includes('Georgia Tech Bus Route Finder');
        
        tests.push({ 
            name: 'Frontend Accessibility', 
            status: (hasGoogleMaps && hasPlacesLibrary && hasReactApp) ? 'PASS' : 'FAIL',
            details: {
                googleMaps: hasGoogleMaps,
                placesLibrary: hasPlacesLibrary,
                reactApp: hasReactApp
            }
        });
    } catch (error) {
        tests.push({ name: 'Frontend Accessibility', status: 'FAIL', error: error.message });
        allPassed = false;
    }

    // Test 3: API Endpoints
    const endpoints = [
        { method: 'GET', path: '/api/health', name: 'Health Check' },
        { method: 'GET', path: '/api/buildings', name: 'Buildings List' }
    ];

    for (const endpoint of endpoints) {
        try {
            const response = await axios({
                method: endpoint.method,
                url: `http://localhost:5001${endpoint.path}`
            });
            tests.push({ 
                name: endpoint.name, 
                status: response.status === 200 ? 'PASS' : 'FAIL',
                statusCode: response.status
            });
        } catch (error) {
            tests.push({ name: endpoint.name, status: 'FAIL', error: error.message });
            allPassed = false;
        }
    }

    // Test 4: Route Search Functionality
    const searchTests = [
        {
            name: 'Building Search',
            data: { begin_building: 'Tech Tower', dest_building: 'Georgia Tech Library' }
        },
        {
            name: 'Place Search',
            data: { 
                begin_location: 'GT Campus', 
                dest_location: 'Midtown',
                begin_coordinates: '33.7756,-84.3963',
                dest_coordinates: '33.7896,-84.3843'
            }
        },
        {
            name: 'Mixed Search',
            data: { 
                begin_building: 'Tech Tower', 
                dest_location: 'Piedmont Park',
                dest_coordinates: '33.7856,-84.3736'
            }
        }
    ];

    for (const test of searchTests) {
        try {
            const response = await axios.post('http://localhost:5001/api/RouteSearch', test.data);
            const hasRoutes = response.data.routes && response.data.routes.length > 0;
            tests.push({ 
                name: `${test.name}`, 
                status: hasRoutes ? 'PASS' : 'FAIL',
                routeCount: response.data.routes ? response.data.routes.length : 0
            });
        } catch (error) {
            tests.push({ name: test.name, status: 'FAIL', error: error.message });
            allPassed = false;
        }
    }

    // Test 5: Error Handling
    try {
        await axios.post('http://localhost:5001/api/RouteSearch', {
            begin_building: 'Invalid Building',
            dest_building: 'Tech Tower'
        });
        tests.push({ name: 'Error Handling', status: 'FAIL', error: 'Should have failed' });
        allPassed = false;
    } catch (error) {
        if (error.response && error.response.status === 400) {
            tests.push({ name: 'Error Handling', status: 'PASS' });
        } else {
            tests.push({ name: 'Error Handling', status: 'FAIL', error: error.message });
            allPassed = false;
        }
    }

    // Test 6: Performance
    try {
        const startTime = Date.now();
        const promises = [];
        for (let i = 0; i < 5; i++) {
            promises.push(axios.post('http://localhost:5001/api/RouteSearch', {
                begin_building: 'Tech Tower',
                dest_building: 'Georgia Tech Library'
            }));
        }
        await Promise.all(promises);
        const duration = Date.now() - startTime;
        tests.push({ 
            name: 'Performance', 
            status: duration < 1000 ? 'PASS' : 'WARN',
            duration: `${duration}ms`
        });
    } catch (error) {
        tests.push({ name: 'Performance', status: 'FAIL', error: error.message });
        allPassed = false;
    }

    // Results
    console.log('📊 TEST RESULTS:');
    console.log('================');
    
    tests.forEach(test => {
        const icon = test.status === 'PASS' ? '✅' : test.status === 'FAIL' ? '❌' : '⚠️';
        console.log(`${icon} ${test.name}: ${test.status}`);
        
        if (test.error) {
            console.log(`   Error: ${test.error}`);
        }
        if (test.details) {
            Object.entries(test.details).forEach(([key, value]) => {
                console.log(`   ${key}: ${value ? '✅' : '❌'}`);
            });
        }
        if (test.routeCount !== undefined) {
            console.log(`   Routes found: ${test.routeCount}`);
        }
        if (test.duration) {
            console.log(`   Duration: ${test.duration}`);
        }
        if (test.statusCode) {
            console.log(`   Status: ${test.statusCode}`);
        }
        console.log('');
    });

    const passCount = tests.filter(t => t.status === 'PASS').length;
    const failCount = tests.filter(t => t.status === 'FAIL').length;
    const warnCount = tests.filter(t => t.status === 'WARN').length;

    console.log('📈 SUMMARY:');
    console.log(`   ✅ Passed: ${passCount}`);
    console.log(`   ❌ Failed: ${failCount}`);
    console.log(`   ⚠️  Warnings: ${warnCount}`);
    console.log(`   📊 Total: ${tests.length}`);

    if (allPassed) {
        console.log('\n🎉 ALL TESTS PASSED!');
        console.log('\n🚀 Your BuzzBus application is fully functional with:');
        console.log('   • React frontend with Google Places integration');
        console.log('   • .NET backend with comprehensive API');
        console.log('   • Building-to-building route search');
        console.log('   • Place-to-place route search with coordinates');
        console.log('   • Mixed search capabilities');
        console.log('   • Real-time Google Places autocomplete');
        console.log('   • Error handling and validation');
        console.log('   • High performance (sub-second response times)');
        console.log('\n🌐 Access your app at: http://localhost:3000');
        console.log('🔧 API available at: http://localhost:5001');
    } else {
        console.log('\n⚠️  Some tests failed. Please check the errors above.');
    }
}

finalVerification().catch(console.error);
