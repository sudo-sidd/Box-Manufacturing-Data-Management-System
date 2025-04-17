/**
 * Box Calculations Module
 * Contains all formulas and calculations for corrugated box manufacturing
 */

// Constants used in calculations
const CONSTANTS = {
  LENGTH_SHRINKAGE_FACTOR: 1.006,
  BREADTH_SHRINKAGE_FACTOR: 1.006,
  HEIGHT_SHRINKAGE_FACTOR: 1.0112,
  FLUTE_TUF: 1.35, // Take-Up Factor for flute papers
  CM_TO_INCH: 2.54,
  PAPER_COST_PER_KG: 80,
  LABOR_COST_PERCENTAGE: 0.3
};

/**
 * Calculate box dimensions with shrinkage
 */
function calculateDimensions(length, breadth, height) {
  const lengthWithShrinkage = length * CONSTANTS.LENGTH_SHRINKAGE_FACTOR;
  const breadthWithShrinkage = breadth * CONSTANTS.BREADTH_SHRINKAGE_FACTOR;
  const heightWithShrinkage = height * CONSTANTS.HEIGHT_SHRINKAGE_FACTOR;
  
  // Calculate flute size
  const fluteSize = (breadth + 0.635) * 1.013575 / 2;
  
  return {
    length: lengthWithShrinkage,
    breadth: breadthWithShrinkage,
    height: heightWithShrinkage,
    fluteSize: fluteSize
  };
}

/**
 * Calculate board sizes in inches
 */
function calculateBoardSizes(length, breadth, height, fluteSize) {
  // Calculate full length in inches
  const fullLengthInches = ((length + breadth) * 2 + 3.5 + 0.5) / CONSTANTS.CM_TO_INCH;
  
  // Calculate half length in inches
  const halfLengthInches = ((length + breadth) + 3.5 + 0.4) / CONSTANTS.CM_TO_INCH;
  
  // Calculate reel sizes
  const reelSize1Up = ((height + fluteSize + fluteSize) + 0.8) / CONSTANTS.CM_TO_INCH;
  const reelSize2Up = (((height + fluteSize + fluteSize) * 2) + 0.8) / CONSTANTS.CM_TO_INCH;
  const reelWidth = (breadth + height) / CONSTANTS.CM_TO_INCH;
  
  return {
    fullLengthInches,
    halfLengthInches,
    reelSize1Up,
    reelSize2Up,
    reelWidth
  };
}

/**
 * Determine UPS (production mode)
 */
function determineUPS(reelWidth, fullLengthInches) {
  if (reelWidth < 20) {
    return "2 board length";
  } else if (reelWidth >= 20 && reelWidth < 40) {
    return "1 board length";
  } else if (reelWidth < 60) {
    return "full length";
  } else if (fullLengthInches > 60) {
    return "half length";
  }
  return "full length"; // Default
}

/**
 * Calculate paper weights based on dimensions and GSM values
 */
function calculatePaperWeights(fullLengthInches, reelWidth, paperGsms) {
  const paperWeights = {};
  const paperArea = fullLengthInches * reelWidth; // in square inches
  
  // Calculate top paper weight
  if (paperGsms.top_paper_gsm > 0) {
    paperWeights.top_paper_weight = (paperArea * paperGsms.top_paper_gsm) / 1550;
  } else {
    paperWeights.top_paper_weight = 0;
  }
  
  // Calculate bottom paper weight
  if (paperGsms.bottom_paper_gsm > 0) {
    paperWeights.bottom_paper_weight = (paperArea * paperGsms.bottom_paper_gsm) / 1550;
  } else {
    paperWeights.bottom_paper_weight = 0;
  }
  
  // Calculate flute paper weight for 5-ply
  if (paperGsms.flute_paper_gsm > 0) {
    paperWeights.flute_paper_weight = (paperArea * paperGsms.flute_paper_gsm * CONSTANTS.FLUTE_TUF) / 1550;
  } else {
    paperWeights.flute_paper_weight = 0;
  }
  
  // Calculate additional papers for 7-ply
  if (paperGsms.flute_paper1_gsm > 0) {
    paperWeights.flute_paper1_weight = (paperArea * paperGsms.flute_paper1_gsm * CONSTANTS.FLUTE_TUF) / 1550;
  } else {
    paperWeights.flute_paper1_weight = 0;
  }
  
  if (paperGsms.middle_paper_gsm > 0) {
    paperWeights.middle_paper_weight = (paperArea * paperGsms.middle_paper_gsm) / 1550;
  } else {
    paperWeights.middle_paper_weight = 0;
  }
  
  if (paperGsms.flute_paper2_gsm > 0) {
    paperWeights.flute_paper2_weight = (paperArea * paperGsms.flute_paper2_gsm * CONSTANTS.FLUTE_TUF) / 1550;
  } else {
    paperWeights.flute_paper2_weight = 0;
  }
  
  // Calculate total material weight - include only non-zero weights
  paperWeights.total_material_weight = Object.entries(paperWeights)
    .filter(([key, value]) => key !== 'total_material_weight' && value > 0)
    .reduce((sum, [key, weight]) => sum + weight, 0);
  
  return paperWeights;
}

/**
 * Calculate production costs
 */
function calculateCosts(paperWeights) {
  const materialCost = paperWeights.total_material_weight * CONSTANTS.PAPER_COST_PER_KG;
  const laborCost = materialCost * CONSTANTS.LABOR_COST_PERCENTAGE;
  const totalCost = materialCost + laborCost;
  
  return {
    material_cost: materialCost,
    labor_cost: laborCost,
    total_cost: totalCost
  };
}

/**
 * Generate explanation for UPS determination
 */
function getUpsReason(reelWidth, fullLengthInches) {
  if (reelWidth < 20) {
    return `Reel Width (${reelWidth.toFixed(2)}") < 20" → 2 board length`;
  } else if (reelWidth >= 20 && reelWidth < 40) {
    return `20" ≤ Reel Width (${reelWidth.toFixed(2)}") < 40" → 1 board length`;
  } else if (reelWidth < 60) {
    return `Reel Width (${reelWidth.toFixed(2)}") < 60" → full length`;
  } else if (fullLengthInches > 60) {
    return `Full Length (${fullLengthInches.toFixed(2)}") > 60" → half length`;
  } else {
    return `Default case → full length`;
  }
}

/**
 * Generate calculation formulas with values for display
 */
function generateCalculationFormulas(length, breadth, height, dimensions, boardSizes, paperGsms, paperWeights, costs) {
  const formulas = {
    dimensions: [],
    boardSizes: [],
    ups: [],
    paperWeights: [],
    costs: []
  };
  
  // Dimension formulas
  formulas.dimensions = [
    `L (cm) = ${length} × ${CONSTANTS.LENGTH_SHRINKAGE_FACTOR} = ${dimensions.length.toFixed(2)}`,
    `B (cm) = ${breadth} × ${CONSTANTS.BREADTH_SHRINKAGE_FACTOR} = ${dimensions.breadth.toFixed(2)}`,
    `H (cm) = ${height} × ${CONSTANTS.HEIGHT_SHRINKAGE_FACTOR} = ${dimensions.height.toFixed(2)}`,
    `F (cm) = (${breadth} + 0.635) × 1.013575 / 2 = ${dimensions.fluteSize.toFixed(2)}`
  ];
  
  // Board size formulas
  formulas.boardSizes = [
    `Length (L") for full length = ((${length}+${breadth}) × 2 + 3.5 + 0.5) / 2.54 = ${boardSizes.fullLengthInches.toFixed(2)}"`,
    `Length (L") for half length = ((${length}+${breadth}) + 3.5 + 0.4) / 2.54 = ${boardSizes.halfLengthInches.toFixed(2)}"`,
    `Reel size (R) for 1 up = ((${height}+${dimensions.fluteSize.toFixed(2)}+${dimensions.fluteSize.toFixed(2)})+0.8) / 2.54 = ${boardSizes.reelSize1Up.toFixed(2)}"`,
    `Reel size (R) for 2 up = (((${height}+${dimensions.fluteSize.toFixed(2)}+${dimensions.fluteSize.toFixed(2)})×2)+0.8) / 2.54 = ${boardSizes.reelSize2Up.toFixed(2)}"`,
    `Reel Width = (${breadth}+${height})/2.54 = ${boardSizes.reelWidth.toFixed(2)}"`
  ];
  
  // UPS determination
  formulas.ups = [
    `Reel Width = ${boardSizes.reelWidth.toFixed(2)}"`,
    `Full Length = ${boardSizes.fullLengthInches.toFixed(2)}"`,
    `UPS Determination: ${getUpsReason(boardSizes.reelWidth, boardSizes.fullLengthInches)}`
  ];
  
  // Paper area calculation
  const paperArea = boardSizes.fullLengthInches * boardSizes.reelWidth;
  formulas.paperWeights.push(`Paper Area = Full Length (${boardSizes.fullLengthInches.toFixed(2)}") × Reel Width (${boardSizes.reelWidth.toFixed(2)}") = ${paperArea.toFixed(2)} in²`);
  
  // Paper weight formulas
  if (paperGsms.top_paper_gsm > 0) {
    formulas.paperWeights.push(`Top Paper Weight = (${paperArea.toFixed(2)} × ${paperGsms.top_paper_gsm}) / 1550 = ${paperWeights.top_paper_weight.toFixed(2)} kg`);
  }
  
  if (paperGsms.bottom_paper_gsm > 0) {
    formulas.paperWeights.push(`Bottom Paper Weight = (${paperArea.toFixed(2)} × ${paperGsms.bottom_paper_gsm}) / 1550 = ${paperWeights.bottom_paper_weight.toFixed(2)} kg`);
  }
  
  if (paperGsms.flute_paper_gsm > 0) {
    formulas.paperWeights.push(`Flute Paper Weight = (${paperArea.toFixed(2)} × ${paperGsms.flute_paper_gsm} × ${CONSTANTS.FLUTE_TUF}) / 1550 = ${paperWeights.flute_paper_weight.toFixed(2)} kg`);
  }
  
  if (paperGsms.flute_paper1_gsm > 0) {
    formulas.paperWeights.push(`Flute Paper 1 Weight = (${paperArea.toFixed(2)} × ${paperGsms.flute_paper1_gsm} × ${CONSTANTS.FLUTE_TUF}) / 1550 = ${paperWeights.flute_paper1_weight.toFixed(2)} kg`);
  }
  
  if (paperGsms.middle_paper_gsm > 0) {
    formulas.paperWeights.push(`Middle Paper Weight = (${paperArea.toFixed(2)} × ${paperGsms.middle_paper_gsm}) / 1550 = ${paperWeights.middle_paper_weight.toFixed(2)} kg`);
  }
  
  if (paperGsms.flute_paper2_gsm > 0) {
    formulas.paperWeights.push(`Flute Paper 2 Weight = (${paperArea.toFixed(2)} × ${paperGsms.flute_paper2_gsm} × ${CONSTANTS.FLUTE_TUF}) / 1550 = ${paperWeights.flute_paper2_weight.toFixed(2)} kg`);
  }
  
  formulas.paperWeights.push(`Total Material Weight = ${paperWeights.total_material_weight.toFixed(2)} kg`);
  
  // Cost formulas
  formulas.costs = [
    `Material Cost = ${paperWeights.total_material_weight.toFixed(2)} kg × ₹${CONSTANTS.PAPER_COST_PER_KG} = ₹${costs.material_cost.toFixed(2)}`,
    `Labor Cost = ₹${costs.material_cost.toFixed(2)} × ${CONSTANTS.LABOR_COST_PERCENTAGE} = ₹${costs.labor_cost.toFixed(2)}`,
    `Total Cost = ₹${costs.material_cost.toFixed(2)} + ₹${costs.labor_cost.toFixed(2)} = ₹${costs.total_cost.toFixed(2)}`
  ];
  
  return formulas;
}

/**
 * Master calculation function
 * Takes inputs and returns complete calculation results
 */
function performBoxCalculations(length, breadth, height, fluteType, numPlies, paperGsms) {
  // Calculate all components
  const dimensions = calculateDimensions(length, breadth, height);
  const boardSizes = calculateBoardSizes(length, breadth, height, dimensions.fluteSize);
  const ups = determineUPS(boardSizes.reelWidth, boardSizes.fullLengthInches);
  const paperWeights = calculatePaperWeights(boardSizes.fullLengthInches, boardSizes.reelWidth, paperGsms);
  const costs = calculateCosts(paperWeights);
  
  // Calculate the paper area
  const paperArea = boardSizes.fullLengthInches * boardSizes.reelWidth;
  
  // Generate calculation formulas with actual values
  const formulas = generateCalculationFormulas(length, breadth, height, dimensions, boardSizes, paperGsms, paperWeights, costs);
  
  // Return complete calculation results
  return {
    dimensions,
    boardSizes,
    ups,
    paperArea,
    paperWeights,
    costs,
    formulas,
    constants: CONSTANTS
  };
}

// Add event listeners when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  const numPliesSelect = document.getElementById('id_num_plies');
  const calculateBtn = document.getElementById('calculate-btn');
  
  // Handle ply selection to show/hide paper requirement fields
  if (numPliesSelect) {
    numPliesSelect.addEventListener('change', updatePaperFieldsVisibility);
    
    // Set default to 3 plies if not already set
    if (!numPliesSelect.value) {
      numPliesSelect.value = "3";
    }
    
    // Call function on page load to set initial state
    updatePaperFieldsVisibility();
  }
  
  // Add calculation button handler
  if (calculateBtn) {
    calculateBtn.addEventListener('click', function() {
      // Get form values
      const length = parseFloat(document.getElementById('id_length').value);
      const breadth = parseFloat(document.getElementById('id_breadth').value);
      const height = parseFloat(document.getElementById('id_height').value);
      const fluteType = document.getElementById('id_flute_type').value;
      const numPlies = parseInt(document.getElementById('id_num_plies').value) || 3;
      
      if (!length || !breadth || !height) {
        alert('Please enter all dimensions');
        return;
      }
      
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
      
      // Perform calculations
      const results = performBoxCalculations(length, breadth, height, fluteType, numPlies, paperGsms);
      
      // Display results
      displayCalculationResults(results);
      
      // Show calculation details section
      document.getElementById('calculation-details').style.display = 'block';
    });
  }
});

// Show/hide additional paper fields based on ply count
function updatePaperFieldsVisibility() {
  const numPlies = parseInt(document.getElementById('id_num_plies').value) || 3;
  const flutePaperFields = document.querySelector('.flute-paper-fields');
  const sevenPlyFields = document.querySelector('.seven-ply-fields');
  
  if (!flutePaperFields || !sevenPlyFields) return;
  
  // Basic logic for showing/hiding sections
  if (numPlies < 5) {
    // For 3-ply, hide both 5-ply and 7-ply fields
    flutePaperFields.style.display = 'none';
    sevenPlyFields.style.display = 'none';
  } else if (numPlies >= 5 && numPlies < 7) {
    // For 5-ply, show only 5-ply fields
    flutePaperFields.style.display = 'block';
    sevenPlyFields.style.display = 'none';
    
    // Enable input fields for 5-ply section
    enableFormFields(flutePaperFields, true);
  } else if (numPlies >= 7) {
    // For 7-ply, hide 5-ply fields and show 7-ply fields
    flutePaperFields.style.display = 'none';
    sevenPlyFields.style.display = 'block';
    
    // Disable 5-ply fields and enable 7-ply fields
    enableFormFields(flutePaperFields, false);
    enableFormFields(sevenPlyFields, true);
  }
}

// Helper function to enable/disable form fields
function enableFormFields(container, enable) {
  const inputs = container.querySelectorAll('input, select, textarea');
  inputs.forEach(input => {
    if (enable) {
      input.removeAttribute('disabled');
      input.classList.remove('disabled-field');
    } else {
      input.setAttribute('disabled', 'disabled');
      input.classList.add('disabled-field');
    }
  });
}

// Display calculation results in the UI
function displayCalculationResults(results) {
  // First create the specifications table
  const resultsHTML = `
    <div class="card">
      <div class="card-header bg-primary text-white">
        <h5>Box Production Specifications</h5>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <h6>Dimensions with Shrinkage</h6>
            <table class="table table-sm">
              <tr>
                <th>Length (cm)</th>
                <td>${results.dimensions.length.toFixed(2)}</td>
              </tr>
              <tr>
                <th>Breadth (cm)</th>
                <td>${results.dimensions.breadth.toFixed(2)}</td>
              </tr>
              <tr>
                <th>Height (cm)</th>
                <td>${results.dimensions.height.toFixed(2)}</td>
              </tr>
              <tr>
                <th>Flute Size (cm)</th>
                <td>${results.dimensions.fluteSize.toFixed(2)}</td>
              </tr>
            </table>
            
            <h6>Board Specifications</h6>
            <table class="table table-sm">
              <tr>
                <th>Full Length (in)</th>
                <td>${results.boardSizes.fullLengthInches.toFixed(2)}</td>
              </tr>
              <tr>
                <th>Half Length (in)</th>
                <td>${results.boardSizes.halfLengthInches.toFixed(2)}</td>
              </tr>
              <tr>
                <th>Reel Size 1-up (in)</th>
                <td>${results.boardSizes.reelSize1Up.toFixed(2)}</td>
              </tr>
              <tr>
                <th>Reel Size 2-up (in)</th>
                <td>${results.boardSizes.reelSize2Up.toFixed(2)}</td>
              </tr>
              <tr>
                <th>UPS (Production Mode)</th>
                <td>${results.ups}</td>
              </tr>
            </table>
          </div>
          
          <div class="col-md-6">
            <h6>Paper Requirements</h6>
            <table class="table table-sm">
              ${Object.entries(results.paperWeights)
                .filter(([key, value]) => key !== 'total_material_weight' && value > 0)
                .map(([key, value]) => `
                  <tr>
                    <th>${key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</th>
                    <td>${value.toFixed(2)} kg</td>
                  </tr>
                `)
                .join('')}
              <tr>
                <th>Total Material Weight</th>
                <td>${results.paperWeights.total_material_weight.toFixed(2)} kg</td>
              </tr>
            </table>
            
            <h6>Cost Estimates</h6>
            <table class="table table-sm">
              <tr>
                <th>Material Cost</th>
                <td>₹${results.costs.material_cost.toFixed(2)}</td>
              </tr>
              <tr>
                <th>Labor Cost</th>
                <td>₹${results.costs.labor_cost.toFixed(2)}</td>
              </tr>
              <tr class="table-primary">
                <th>Total Production Cost</th>
                <td>₹${results.costs.total_cost.toFixed(2)}</td>
              </tr>
            </table>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Update the results div
  document.getElementById('calculation-results').innerHTML = resultsHTML;
  
  // Update constants display
  document.getElementById('length-shrinkage-factor').textContent = CONSTANTS.LENGTH_SHRINKAGE_FACTOR;
  document.getElementById('breadth-shrinkage-factor').textContent = CONSTANTS.BREADTH_SHRINKAGE_FACTOR;
  document.getElementById('height-shrinkage-factor').textContent = CONSTANTS.HEIGHT_SHRINKAGE_FACTOR;
  document.getElementById('flute-tuf').textContent = CONSTANTS.FLUTE_TUF;
  document.getElementById('cm-to-in-factor').textContent = CONSTANTS.CM_TO_INCH;
  document.getElementById('paper-cost-per-kg').textContent = CONSTANTS.PAPER_COST_PER_KG;
  document.getElementById('labor-cost-percentage').textContent = (CONSTANTS.LABOR_COST_PERCENTAGE * 100) + '%';
  
  // Update formula displays
  // Dimension formulas
  const dimensionFormulas = document.getElementById('dimension-formulas');
  if (dimensionFormulas) {
    dimensionFormulas.innerHTML = results.formulas.dimensions
      .map(formula => `<div class="calculation-formula">${formula}</div>`)
      .join('');
  }
  
  // Board size formulas
  const boardSizeFormulas = document.getElementById('board-size-formulas');
  if (boardSizeFormulas) {
    boardSizeFormulas.innerHTML = results.formulas.boardSizes
      .map(formula => `<div class="calculation-formula">${formula}</div>`)
      .join('');
  }
  
  // UPS formulas
  const upsFormulas = document.getElementById('ups-formulas');
  if (upsFormulas) {
    upsFormulas.innerHTML = results.formulas.ups
      .map(formula => `<div class="calculation-formula">${formula}</div>`)
      .join('');
  }
  
  // Paper weight formulas
  const paperWeightFormulas = document.getElementById('paper-weight-formulas');
  if (paperWeightFormulas) {
    paperWeightFormulas.innerHTML = results.formulas.paperWeights
      .map(formula => `<div class="calculation-formula">${formula}</div>`)
      .join('');
  }
  
  // Cost formulas
  const costFormulas = document.getElementById('cost-formulas');
  if (costFormulas) {
    costFormulas.innerHTML = results.formulas.costs
      .map(formula => `<div class="calculation-formula">${formula}</div>`)
      .join('');
  }
}