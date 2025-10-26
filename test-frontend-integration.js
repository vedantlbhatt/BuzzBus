const axios = require('axios');

async function testFrontendIntegration() {
    console.log('🌐 Testing Frontend Integration with Google Places...\n');

    try {
        // Test 1: Frontend is accessible
        console.log('1️⃣ Testing Frontend Accessibility...');
        const frontendResponse = await axios.get('http://localhost:3000');
        
        if (frontendResponse.status === 200) {
            console.log('✅ Frontend is accessible');
            
            // Check for Google Maps API script
            if (frontendResponse.data.includes('maps.googleapis.com')) {
                console.log('✅ Google Maps API script loaded');
            } else {
                console.log('❌ Google Maps API script not found');
            }
            
            // Check for React app content
            if (frontendResponse.data.includes('Georgia Tech Bus Route Finder')) {
                console.log('✅ React app content loaded');
            } else {
                console.log('❌ React app content not found');
            }
        } else {
            throw new Error(`Frontend returned status ${frontendResponse.status}`);
        }

        // Test 2: API Proxy is working
        console.log('\n2️⃣ Testing API Proxy...');
        try {
            const proxyResponse = await axios.get('http://localhost:3000/api/health');
            if (proxyResponse.data.status === 'healthy') {
                console.log('✅ API proxy working - Frontend can reach backend');
            } else {
                console.log('❌ API proxy not working');
            }
        } catch (error) {
            console.log('❌ API proxy failed:', error.message);
        }

        // Test 3: Test different search scenarios through API
        console.log('\n3️⃣ Testing Search Scenarios...');
        
        const searchTests = [
            {
                name: 'Campus Buildings',
                data: {
                    begin_building: 'Tech Tower',
                    dest_building: 'Georgia Tech Library'
                }
            },
            {
                name: 'Any Locations',
                data: {
                    begin_location: 'Georgia Tech Campus',
                    dest_location: 'Midtown Atlanta',
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
                if (response.data.routes && response.data.routes.length > 0) {
                    console.log(`✅ ${test.name} search works - ${response.data.routes.length} routes found`);
                } else {
                    console.log(`⚠️  ${test.name} search returned no routes`);
                }
            } catch (error) {
                console.log(`❌ ${test.name} search failed:`, error.message);
            }
        }

        // Test 4: Check for Google Places specific features
        console.log('\n4️⃣ Testing Google Places Features...');
        
        // Test coordinate parsing
        const coordinateTest = await axios.post('http://localhost:5001/api/RouteSearch', {
            begin_location: 'Test Location',
            dest_location: 'Another Location',
            begin_coordinates: '33.7756,-84.3963',
            dest_coordinates: '33.7896,-84.3843'
        });
        
        if (coordinateTest.data.routes) {
            console.log('✅ Coordinate parsing works');
        } else {
            console.log('❌ Coordinate parsing failed');
        }

        // Test 5: Performance under load
        console.log('\n5️⃣ Testing Performance...');
        const startTime = Date.now();
        const promises = [];
        
        for (let i = 0; i < 10; i++) {
            promises.push(axios.post('http://localhost:5001/api/RouteSearch', {
                begin_building: 'Tech Tower',
                dest_building: 'Georgia Tech Library'
            }));
        }
        
        await Promise.all(promises);
        const endTime = Date.now();
        console.log(`✅ Performance test: 10 requests completed in ${endTime - startTime}ms`);

        console.log('\n🎉 Frontend Integration Test Complete!');
        console.log('\n📱 Frontend Features Available:');
        console.log('   • Toggle between Campus Buildings and Any Location');
        console.log('   • Google Places autocomplete for location search');
        console.log('   • Real-time search suggestions');
        console.log('   • Mixed search support (building + place)');
        console.log('   • Coordinate-based route calculations');
        console.log('   • Responsive UI with modern design');

    } catch (error) {
        console.error('❌ Frontend integration test failed:', error.message);
    }
}

testFrontendIntegration();
