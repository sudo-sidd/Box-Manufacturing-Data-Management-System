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
                top_paper_gsm: parseFloat(document.getElementById('id_top_paper_gsm').value) || 120,
                bottom_paper_gsm: parseFloat(document.getElementById('id_bottom_paper_gsm').value) || 120
            };
            
            if (numPlies >= 5) {
                paperGsms.flute_paper_gsm = parseFloat(document.getElementById('id_flute_paper_gsm').value) || 100;
            }
            
            if (numPlies === 7) {
                paperGsms.flute_paper1_gsm = parseFloat(document.getElementById('id_flute_paper1_gsm').value) || 100;
                paperGsms.middle_paper_gsm = parseFloat(document.getElementById('id_middle_paper_gsm').value) || 100;
                paperGsms.flute_paper2_gsm = parseFloat(document.getElementById('id_flute_paper2_gsm').value) || 100;
            }
            
            // Make AJAX request to get calculations
            fetch(`/finished-goods/calculations/?length=${length}&breadth=${breadth}&height=${height}&flute_type=${fluteType}&num_plies=${numPlies}&${new URLSearchParams(paperGsms)}`)
                .then(response => response.json())
                .then(data => {
                    displayResults(data);
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
    function displayResults(data) {
        let html = `
            <div class="card mt-3">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">Box Production Specifications</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Dimensions with Shrinkage</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td>Length (cm)</td>
                                    <td>${data.dimensions.length.toFixed(2)}</td>
                                </tr>
                                <tr>
                                    <td>Breadth (cm)</td>
                                    <td>${data.dimensions.breadth.toFixed(2)}</td>
                                </tr>
                                <tr>
                                    <td>Height (cm)</td>
                                    <td>${data.dimensions.height.toFixed(2)}</td>
                                </tr>
                                <tr>
                                    <td>Flute Size (cm)</td>
                                    <td>${data.dimensions.flute_size.toFixed(2)}</td>
                                </tr>
                            </table>
                            
                            <h6 class="mt-3">Board Specifications</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td>Full Length (in)</td>
                                    <td>${data.board_sizes.full_length_in.toFixed(2)}</td>
                                </tr>
                                <tr>
                                    <td>Half Length (in)</td>
                                    <td>${data.board_sizes.half_length_in.toFixed(2)}</td>
                                </tr>
                                <tr>
                                    <td>Reel Size 1-up (in)</td>
                                    <td>${data.board_sizes.reel_size_1up.toFixed(2)}</td>
                                </tr>
                                <tr>
                                    <td>Reel Size 2-up (in)</td>
                                    <td>${data.board_sizes.reel_size_2up.toFixed(2)}</td>
                                </tr>
                                <tr>
                                    <td>UPS (Production Mode)</td>
                                    <td>${data.ups}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <div class="col-md-6">
                            <h6>Paper Requirements</h6>
                            <table class="table table-sm">`;
        
        // Add paper weights based on available data
        Object.entries(data.paper_weights).forEach(([key, value]) => {
            const displayName = key.replace('_', ' ').replace(/^\w/, c => c.toUpperCase());
            html += `<tr>
                        <td>${displayName}</td>
                        <td>${value} kg</td>
                     </tr>`;
        });
        
        html += `</table>
                            
                            <h6 class="mt-3">Cost Estimates</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td>Material Cost</td>
                                    <td>₹${data.cost_estimates.material_cost}</td>
                                </tr>
                                <tr>
                                    <td>Labor Cost</td>
                                    <td>₹${data.cost_estimates.labor_cost}</td>
                                </tr>
                                <tr class="font-weight-bold">
                                    <td>Total Production Cost</td>
                                    <td>₹${data.cost_estimates.total_cost}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        resultsDiv.innerHTML = html;
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