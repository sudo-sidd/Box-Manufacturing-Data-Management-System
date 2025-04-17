document.addEventListener('DOMContentLoaded', function() {
    // Cache DOM elements
    const lengthInput = document.getElementById('id_length');
    const breadthInput = document.getElementById('id_breadth');
    const heightInput = document.getElementById('id_height');
    const fluteTypeSelect = document.getElementById('id_flute_type');
    const numPliesSelect = document.getElementById('id_num_plies');
    const calculateBtn = document.getElementById('calculate-btn');
    const resultsDiv = document.getElementById('calculation-results');
    
    // Handle ply selection to show/hide paper requirement fields
    if (numPliesSelect) {
        numPliesSelect.addEventListener('change', function() {
            const plyValue = parseInt(this.value);
            
            // Show/hide 5-ply specific fields
            const flutePaperFields = document.querySelectorAll('.flute-paper-fields');
            flutePaperFields.forEach(field => {
                field.style.display = (plyValue >= 5) ? 'block' : 'none';
            });
            
            // Show/hide 7-ply specific fields
            const sevenPlyFields = document.querySelectorAll('.seven-ply-fields');
            sevenPlyFields.forEach(field => {
                field.style.display = (plyValue === 7) ? 'block' : 'none';
            });
        });
        
        // Trigger change event to set initial state
        numPliesSelect.dispatchEvent(new Event('change'));
    }
    
    // Function to calculate box dimensions and requirements
    function calculateBoxRequirements() {
        const length = parseFloat(lengthInput.value) || 0;
        const breadth = parseFloat(breadthInput.value) || 0;
        const height = parseFloat(heightInput.value) || 0;
        const fluteType = fluteTypeSelect.value;
        const numPlies = parseInt(numPliesSelect.value) || 3;
        
        if (length && breadth && height) {
            // Collect GSM values based on ply count
            const paperGsms = {
                top_paper_gsm: parseFloat(document.getElementById('id_top_paper_gsm').value) || 0,
                bottom_paper_gsm: parseFloat(document.getElementById('id_bottom_paper_gsm').value) || 0
            };
            
            if (numPlies >= 5) {
                paperGsms.flute_paper_gsm = parseFloat(document.getElementById('id_flute_paper_gsm').value) || 0;
            }
            
            if (numPlies === 7) {
                paperGsms.flute_paper1_gsm = parseFloat(document.getElementById('id_flute_paper1_gsm').value) || 0;
                paperGsms.middle_paper_gsm = parseFloat(document.getElementById('id_middle_paper_gsm').value) || 0;
                paperGsms.flute_paper2_gsm = parseFloat(document.getElementById('id_flute_paper2_gsm').value) || 0;
            }
            
            // Make AJAX request to get calculations
            fetch(`/finished-goods/calculations/?length=${length}&breadth=${breadth}&height=${height}&flute_type=${fluteType}&num_plies=${numPlies}&${new URLSearchParams(paperGsms)}`)
                .then(response => response.json())
                .then(data => {
                    displayCalculationResults(data);
                })
                .catch(error => {
                    console.error('Error calculating box requirements:', error);
                    resultsDiv.innerHTML = '<div class="alert alert-danger">Error calculating requirements.</div>';
                });
        } else {
            resultsDiv.innerHTML = '<div class="alert alert-warning">Please enter all dimensions.</div>';
        }
    }
    
    // Display calculation results
    function displayCalculationResults(data) {
        // Show the results container
        document.getElementById('results-container').style.display = 'flex';
        
        // Update dimensions
        document.getElementById('length_with_shrinkage').textContent = data.dimensions.length.toFixed(2) + ' cm';
        document.getElementById('breadth_with_shrinkage').textContent = data.dimensions.breadth.toFixed(2) + ' cm';
        document.getElementById('height_with_shrinkage').textContent = data.dimensions.height.toFixed(2) + ' cm';
        document.getElementById('flute_size').textContent = data.dimensions.flute_size.toFixed(2) + ' cm';
        
        // Update board specs
        document.getElementById('full_length_in').textContent = data.board_sizes.full_length_in.toFixed(2) + ' in';
        document.getElementById('half_length_in').textContent = data.board_sizes.half_length_in.toFixed(2) + ' in';
        document.getElementById('reel_size_1up').textContent = data.board_sizes.reel_size_1up.toFixed(2) + ' in';
        document.getElementById('reel_size_2up').textContent = data.board_sizes.reel_size_2up.toFixed(2) + ' in';
        document.getElementById('ups').textContent = data.ups;
        
        // Clear existing rows first
        const paperTable = document.getElementById('paper_requirements_table').querySelector('tbody');
        paperTable.innerHTML = '';
        
        // Add all paper requirements with both single and bulk calculations
        const paperWeights = data.paper_weights;
        
        // Create rows for all paper types in the response
        Object.entries(paperWeights).forEach(([key, value]) => {
            const displayName = key
                .replace(/_/g, ' ')
                .replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase())
                .replace('Weight', '');
                
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${displayName}:</td>
                <td>${value.toFixed(2)} kg</td>
                <td>${(value * 1000).toFixed(2)} kg</td>
            `;
            paperTable.appendChild(row);
        });
        
        // Update cost estimates
        document.getElementById('material_cost').textContent = '₹' + data.cost_estimates.material_cost.toFixed(2);
        document.getElementById('labor_cost').textContent = '₹' + data.cost_estimates.labor_cost.toFixed(2);
        document.getElementById('total_cost').textContent = '₹' + data.cost_estimates.total_cost.toFixed(2);
        
        document.getElementById('material_cost_bulk').textContent = '₹' + (data.cost_estimates.material_cost * 1000).toFixed(2);
        document.getElementById('labor_cost_bulk').textContent = '₹' + (data.cost_estimates.labor_cost * 1000).toFixed(2);
        document.getElementById('total_cost_bulk').textContent = '₹' + (data.cost_estimates.total_cost * 1000).toFixed(2);
    }
    
    // Add event listeners
    if (calculateBtn) {
        calculateBtn.addEventListener('click', function(e) {
            e.preventDefault();
            calculateBoxRequirements();
        });
    }
    
    // Add live calculation triggers for input fields
    const dimensionInputs = [lengthInput, breadthInput, heightInput];
    dimensionInputs.forEach(input => {
        if (input) {
            input.addEventListener('change', function() {
                if (this.value && this.value > 0 && 
                    lengthInput.value && breadthInput.value && heightInput.value) {
                    calculateBoxRequirements();
                }
            });
        }
    });
});