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
 * Using formula: Weight = (L" x R) x GSM / 1550
 * For flute papers, multiply by TUF (Take-Up Factor)
 */
function calculatePaperWeights(fullLengthInches, reelWidth, paperGsms, paperPrices = {}) {
  const paperWeights = {};
  const paperCosts = {};
  const paperArea = fullLengthInches * reelWidth; // in square inches (L" x R)
  
  // Calculate top paper weight and cost
  if (paperGsms.top_paper_gsm > 0) {
    // Updated formula: (L" x R) x GSM / 1550
    paperWeights.top_paper_weight = (paperArea * paperGsms.top_paper_gsm) / 1550;
    const topPaperPrice = paperPrices.top_paper_price || CONSTANTS.PAPER_COST_PER_KG;
    paperCosts.top_paper_cost = paperWeights.top_paper_weight * topPaperPrice;
  } else {
    paperWeights.top_paper_weight = 0;
    paperCosts.top_paper_cost = 0;
  }
  
  // Calculate bottom paper weight and cost
  if (paperGsms.bottom_paper_gsm > 0) {
    // Updated formula: (L" x R) x GSM / 1550
    paperWeights.bottom_paper_weight = (paperArea * paperGsms.bottom_paper_gsm) / 1550;
    const bottomPaperPrice = paperPrices.bottom_paper_price || CONSTANTS.PAPER_COST_PER_KG;
    paperCosts.bottom_paper_cost = paperWeights.bottom_paper_weight * bottomPaperPrice;
  } else {
    paperWeights.bottom_paper_weight = 0;
    paperCosts.bottom_paper_cost = 0;
  }
  
  // Calculate flute paper weight and cost for 5-ply
  if (paperGsms.flute_paper_gsm > 0) {
    // Updated formula: (L" x R) x GSM x TUF / 1550
    paperWeights.flute_paper_weight = (paperArea * paperGsms.flute_paper_gsm * CONSTANTS.FLUTE_TUF) / 1550;
    const flutePaperPrice = paperPrices.flute_paper_price || CONSTANTS.PAPER_COST_PER_KG;
    paperCosts.flute_paper_cost = paperWeights.flute_paper_weight * flutePaperPrice;
  } else {
    paperWeights.flute_paper_weight = 0;
    paperCosts.flute_paper_cost = 0;
  }
  
  // Calculate additional papers for 7-ply
  if (paperGsms.flute_paper1_gsm > 0) {
    // Updated formula: (L" x R) x GSM x TUF / 1550
    paperWeights.flute_paper1_weight = (paperArea * paperGsms.flute_paper1_gsm * CONSTANTS.FLUTE_TUF) / 1550;
    const flute1PaperPrice = paperPrices.flute_paper1_price || CONSTANTS.PAPER_COST_PER_KG;
    paperCosts.flute_paper1_cost = paperWeights.flute_paper1_weight * flute1PaperPrice;
  } else {
    paperWeights.flute_paper1_weight = 0;
    paperCosts.flute_paper1_cost = 0;
  }
  
  if (paperGsms.middle_paper_gsm > 0) {
    // Updated formula: (L" x R) x GSM / 1550 (no TUF for middle paper)
    paperWeights.middle_paper_weight = (paperArea * paperGsms.middle_paper_gsm) / 1550;
    const middlePaperPrice = paperPrices.middle_paper_price || CONSTANTS.PAPER_COST_PER_KG;
    paperCosts.middle_paper_cost = paperWeights.middle_paper_weight * middlePaperPrice;
  } else {
    paperWeights.middle_paper_weight = 0;
    paperCosts.middle_paper_cost = 0;
  }
  
  if (paperGsms.flute_paper2_gsm > 0) {
    // Updated formula: (L" x R) x GSM x TUF / 1550
    paperWeights.flute_paper2_weight = (paperArea * paperGsms.flute_paper2_gsm * CONSTANTS.FLUTE_TUF) / 1550;
    const flute2PaperPrice = paperPrices.flute_paper2_price || CONSTANTS.PAPER_COST_PER_KG;
    paperCosts.flute_paper2_cost = paperWeights.flute_paper2_weight * flute2PaperPrice;
  } else {
    paperWeights.flute_paper2_weight = 0;
    paperCosts.flute_paper2_cost = 0;
  }
  
  // Calculate total material weight - include only non-zero weights
  paperWeights.total_material_weight = Object.entries(paperWeights)
    .filter(([key, value]) => key !== 'total_material_weight' && value > 0)
    .reduce((sum, [key, weight]) => sum + weight, 0);
  
  // Calculate total material cost
  paperCosts.total_material_cost = Object.values(paperCosts).reduce((sum, cost) => sum + cost, 0);
  
  return {
    weights: paperWeights,
    costs: paperCosts,
    totalWeight: paperWeights.total_material_weight,
    totalCost: paperCosts.total_material_cost
  };
}

/**
 * Calculate production costs
 */
function calculateCosts(paperCalculation, numBoxes = 1) {
  const materialCost = paperCalculation.totalCost;
  const laborCost = materialCost * CONSTANTS.LABOR_COST_PERCENTAGE;
  const totalCostPerBox = materialCost + laborCost;
  const totalOrderCost = totalCostPerBox * numBoxes;
  
  return {
    material_cost: materialCost,
    labor_cost: laborCost,
    cost_per_box: totalCostPerBox,
    total_order_cost: totalOrderCost,
    num_boxes: numBoxes
  };
}

/**
 * Generate explanation for UPS determination
 */
function getUpsReason(reelWidth, fullLengthInches) {
  if (reelWidth < 20) {
    return `Reel Width (${reelWidth.toFixed(4)}") < 20" → 2 board length`;
  } else if (reelWidth >= 20 && reelWidth < 40) {
    return `20" ≤ Reel Width (${reelWidth.toFixed(4)}") < 40" → 1 board length`;
  } else if (reelWidth < 60) {
    return `Reel Width (${reelWidth.toFixed(4)}") < 60" → full length`;
  } else if (fullLengthInches > 60) {
    return `Full Length (${fullLengthInches.toFixed(4)}") > 60" → half length`;
  } else {
    return `Default case → full length`;
  }
}

/**
 * Generate calculation formulas with values for display
 */
function generateCalculationFormulas(length, breadth, height, dimensions, boardSizes, paperGsms, paperCalculation, costs) {
  const formulas = {
    dimensions: [],
    boardSizes: [],
    ups: [],
    paperWeights: [],
    costs: []
  };
  
  // Dimension formulas
  formulas.dimensions = [
    `L (cm) = ${length} × ${CONSTANTS.LENGTH_SHRINKAGE_FACTOR} = ${dimensions.length.toFixed(4)}`,
    `B (cm) = ${breadth} × ${CONSTANTS.BREADTH_SHRINKAGE_FACTOR} = ${dimensions.breadth.toFixed(4)}`,
    `H (cm) = ${height} × ${CONSTANTS.HEIGHT_SHRINKAGE_FACTOR} = ${dimensions.height.toFixed(4)}`,
    `F (cm) = (${breadth} + 0.635) × 1.013575 / 2 = ${dimensions.fluteSize.toFixed(4)}`
  ];
  
  // Board size formulas
  formulas.boardSizes = [
    `Length (L") for full length = ((${length}+${breadth}) × 2 + 3.5 + 0.5) / 2.54 = ${boardSizes.fullLengthInches.toFixed(4)}"`,
    `Length (L") for half length = ((${length}+${breadth}) + 3.5 + 0.4) / 2.54 = ${boardSizes.halfLengthInches.toFixed(4)}"`,
    `Reel size (R) for 1 up = ((${height}+${dimensions.fluteSize.toFixed(4)}+${dimensions.fluteSize.toFixed(4)})+0.8) / 2.54 = ${boardSizes.reelSize1Up.toFixed(4)}"`,
    `Reel size (R) for 2 up = (((${height}+${dimensions.fluteSize.toFixed(4)}+${dimensions.fluteSize.toFixed(4)})×2)+0.8) / 2.54 = ${boardSizes.reelSize2Up.toFixed(4)}"`,
    `Reel Width = (${breadth}+${height})/2.54 = ${boardSizes.reelWidth.toFixed(4)}"`
  ];
  
  // UPS determination
  formulas.ups = [
    `Reel Width = ${boardSizes.reelWidth.toFixed(4)}"`,
    `Full Length = ${boardSizes.fullLengthInches.toFixed(4)}"`,
    `UPS Determination: ${getUpsReason(boardSizes.reelWidth, boardSizes.fullLengthInches)}`
  ];
  
  // Paper area calculation
  const paperArea = boardSizes.fullLengthInches * boardSizes.reelWidth;
  formulas.paperWeights.push(`Paper Area = Full Length (${boardSizes.fullLengthInches.toFixed(4)}") × Reel Width (${boardSizes.reelWidth.toFixed(4)}") = ${paperArea.toFixed(4)} in²`);
  
  // Paper weight formulas using formula: (L" x R) x GSM / 1550
  if (paperGsms.top_paper_gsm > 0) {
    formulas.paperWeights.push(`Top Paper Weight = (${paperArea.toFixed(4)} × ${paperGsms.top_paper_gsm}) / 1550 = ${paperCalculation.weights.top_paper_weight.toFixed(4)} kg`);
    formulas.paperWeights.push(`Top Paper Cost = ${paperCalculation.weights.top_paper_weight.toFixed(4)} kg × ₹${CONSTANTS.PAPER_COST_PER_KG} = ₹${paperCalculation.costs.top_paper_cost.toFixed(4)}`);
  }
  
  if (paperGsms.bottom_paper_gsm > 0) {
    formulas.paperWeights.push(`Bottom Paper Weight = (${paperArea.toFixed(4)} × ${paperGsms.bottom_paper_gsm}) / 1550 = ${paperCalculation.weights.bottom_paper_weight.toFixed(4)} kg`);
    formulas.paperWeights.push(`Bottom Paper Cost = ${paperCalculation.weights.bottom_paper_weight.toFixed(4)} kg × ₹${CONSTANTS.PAPER_COST_PER_KG} = ₹${paperCalculation.costs.bottom_paper_cost.toFixed(4)}`);
  }
  
  if (paperGsms.flute_paper_gsm > 0) {
    formulas.paperWeights.push(`Flute Paper Weight = (${paperArea.toFixed(4)} × ${paperGsms.flute_paper_gsm} × ${CONSTANTS.FLUTE_TUF}) / 1550 = ${paperCalculation.weights.flute_paper_weight.toFixed(4)} kg`);
    formulas.paperWeights.push(`Flute Paper Cost = ${paperCalculation.weights.flute_paper_weight.toFixed(4)} kg × ₹${CONSTANTS.PAPER_COST_PER_KG} = ₹${paperCalculation.costs.flute_paper_cost.toFixed(4)}`);
  }
  
  if (paperGsms.flute_paper1_gsm > 0) {
    formulas.paperWeights.push(`Flute Paper 1 Weight = (${paperArea.toFixed(4)} × ${paperGsms.flute_paper1_gsm} × ${CONSTANTS.FLUTE_TUF}) / 1550 = ${paperCalculation.weights.flute_paper1_weight.toFixed(4)} kg`);
    formulas.paperWeights.push(`Flute Paper 1 Cost = ${paperCalculation.weights.flute_paper1_weight.toFixed(4)} kg × ₹${CONSTANTS.PAPER_COST_PER_KG} = ₹${paperCalculation.costs.flute_paper1_cost.toFixed(4)}`);
  }
  
  if (paperGsms.middle_paper_gsm > 0) {
    formulas.paperWeights.push(`Middle Paper Weight = (${paperArea.toFixed(4)} × ${paperGsms.middle_paper_gsm}) / 1550 = ${paperCalculation.weights.middle_paper_weight.toFixed(4)} kg`);
    formulas.paperWeights.push(`Middle Paper Cost = ${paperCalculation.weights.middle_paper_weight.toFixed(4)} kg × ₹${CONSTANTS.PAPER_COST_PER_KG} = ₹${paperCalculation.costs.middle_paper_cost.toFixed(4)}`);
  }
  
  if (paperGsms.flute_paper2_gsm > 0) {
    formulas.paperWeights.push(`Flute Paper 2 Weight = (${paperArea.toFixed(4)} × ${paperGsms.flute_paper2_gsm} × ${CONSTANTS.FLUTE_TUF}) / 1550 = ${paperCalculation.weights.flute_paper2_weight.toFixed(4)} kg`);
    formulas.paperWeights.push(`Flute Paper 2 Cost = ${paperCalculation.weights.flute_paper2_weight.toFixed(4)} kg × ₹${CONSTANTS.PAPER_COST_PER_KG} = ₹${paperCalculation.costs.flute_paper2_cost.toFixed(4)}`);
  }
  
  formulas.paperWeights.push(`Total Material Weight = ${paperCalculation.totalWeight.toFixed(4)} kg`);
  formulas.paperWeights.push(`Total Material Cost = ₹${paperCalculation.totalCost.toFixed(4)}`);
  
  // Cost formulas
  formulas.costs = [
    `Material Cost = ₹${costs.material_cost.toFixed(4)}`,
    `Labor Cost = ₹${costs.material_cost.toFixed(4)} × ${CONSTANTS.LABOR_COST_PERCENTAGE} = ₹${costs.labor_cost.toFixed(4)}`,
    `Total Cost Per Box = ₹${costs.material_cost.toFixed(4)} + ₹${costs.labor_cost.toFixed(4)} = ₹${costs.cost_per_box.toFixed(4)}`
  ];

  if (costs.num_boxes > 1) {
    formulas.costs.push(`Total Order Cost (${costs.num_boxes} boxes) = ₹${costs.cost_per_box.toFixed(4)} × ${costs.num_boxes} = ₹${costs.total_order_cost.toFixed(4)}`);
  }
  
  return formulas;
}

/**
 * Master calculation function
 * Takes inputs and returns complete calculation results
 */
function performBoxCalculations(length, breadth, height, fluteType, numPlies, paperGsms, numBoxes = 1) {
  // Calculate all components
  const dimensions = calculateDimensions(length, breadth, height);
  const boardSizes = calculateBoardSizes(length, breadth, height, dimensions.fluteSize);
  const ups = determineUPS(boardSizes.reelWidth, boardSizes.fullLengthInches);
  const paperCalculation = calculatePaperWeights(boardSizes.fullLengthInches, boardSizes.reelWidth, paperGsms);
  const costs = calculateCosts(paperCalculation, numBoxes);
  
  // Calculate the paper area
  const paperArea = boardSizes.fullLengthInches * boardSizes.reelWidth;
  
  // Generate calculation formulas with actual values
  const formulas = generateCalculationFormulas(length, breadth, height, dimensions, boardSizes, paperGsms, paperCalculation, costs);
  
  // Return complete calculation results
  return {
    dimensions,
    boardSizes: {
      ...boardSizes,
      full_length_in: boardSizes.fullLengthInches,
      half_length_in: boardSizes.halfLengthInches
    },
    ups,
    paperArea,
    paper_weights: paperCalculation.weights,
    total_material_weight: paperCalculation.totalWeight,
    cost_estimates: costs,
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
      const numBoxes = parseInt(document.getElementById('id_num_boxes')?.value) || 1;
      
      if (!length || !breadth || !height) {
        alert('Please enter all dimensions');
        return;
      }
      
      // Calculate dimensions with shrinkage
      const dimensions = calculateDimensions(length, breadth, height);
      
      // Calculate board sizes
      const boardSizes = calculateBoardSizes(length, breadth, height, dimensions.fluteSize);
      
      // Determine UPS
      const ups = determineUPS(boardSizes.reelWidth, boardSizes.fullLengthInches);
      
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
      
      // Calculate paper weights and costs
      const paperCalculation = calculatePaperWeights(boardSizes.fullLengthInches, boardSizes.reelWidth, paperGsms);
      
      // Calculate production costs
      const costs = calculateCosts(paperCalculation, numBoxes);
      
      // Generate calculation formulas
      const formulas = generateCalculationFormulas(length, breadth, height, dimensions, boardSizes, paperGsms, paperCalculation, costs);
      
      // Create results object with the same structure as the server response
      const results = {
        dimensions,
        boardSizes: {
          ...boardSizes,
          full_length_in: boardSizes.fullLengthInches,
          half_length_in: boardSizes.halfLengthInches
        },
        ups,
        paperArea: boardSizes.fullLengthInches * boardSizes.reelWidth,
        paper_weights: paperCalculation.weights,
        total_material_weight: paperCalculation.totalWeight,
        cost_estimates: costs,
        formulas,
        constants: CONSTANTS
      };
      
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
  // Create results HTML using the same structure as before but with updated data
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
                <td>${results.dimensions.length.toFixed(4)}</td>
              </tr>
              <tr>
                <th>Breadth (cm)</th>
                <td>${results.dimensions.breadth.toFixed(4)}</td>
              </tr>
              <tr>
                <th>Height (cm)</th>
                <td>${results.dimensions.height.toFixed(4)}</td>
              </tr>
              <tr>
                <th>Flute Size (cm)</th>
                <td>${results.dimensions.fluteSize.toFixed(4)}</td>
              </tr>
            </table>
            
            <h6>Board Specifications</h6>
            <table class="table table-sm">
              <tr>
                <th>Full Length (in)</th>
                <td>${results.boardSizes.full_length_in.toFixed(4)}</td>
              </tr>
              <tr>
                <th>Half Length (in)</th>
                <td>${results.boardSizes.half_length_in.toFixed(4)}</td>
              </tr>
              <tr>
                <th>Reel Size 1-up (in)</th>
                <td>${results.boardSizes.reelSize1Up.toFixed(4)}</td>
              </tr>
              <tr>
                <th>Reel Size 2-up (in)</th>
                <td>${results.boardSizes.reelSize2Up.toFixed(4)}</td>
              </tr>
              <tr>
                <th>Reel Width (in)</th>
                <td>${results.boardSizes.reelWidth.toFixed(4)}</td>
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
              <tr>
                <th>Paper Area</th>
                <td>${results.paperArea.toFixed(6)} in²</td>
              </tr>
              ${Object.entries(results.paper_weights)
                .filter(([key, value]) => key !== 'total_material_weight' && value > 0)
                .map(([key, value]) => `
                  <tr>
                    <th>${key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</th>
                    <td>${value.toFixed(6)} kg</td>
                  </tr>
                `)
                .join('')}
              <tr>
                <th>Total Material Weight</th>
                <td>${results.total_material_weight.toFixed(6)} kg</td>
              </tr>
            </table>
            
            <h6>Cost Estimates</h6>
            <table class="table table-sm">
              <tr>
                <th>Material Cost</th>
                <td>₹${results.cost_estimates.material_cost.toFixed(4)}</td>
              </tr>
              <tr>
                <th>Labor Cost</th>
                <td>₹${results.cost_estimates.labor_cost.toFixed(4)}</td>
              </tr>
              <tr class="table-primary">
                <th>Cost Per Box</th>
                <td>₹${results.cost_estimates.cost_per_box.toFixed(4)}</td>
              </tr>
              ${results.cost_estimates.num_boxes > 1 ? `
              <tr class="table-info">
                <th>Total Order Cost (${results.cost_estimates.num_boxes} boxes)</th>
                <td>₹${results.cost_estimates.total_order_cost.toFixed(4)}</td>
              </tr>
              ` : ''}
            </table>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Update the results div
  document.getElementById('calculation-results').innerHTML = resultsHTML;
  
  // Update formula displays (as before)
  const dimensionFormulas = document.getElementById('dimension-formulas');
  if (dimensionFormulas) {
    dimensionFormulas.innerHTML = results.formulas.dimensions
      .map(formula => `<div class="calculation-formula">${formula}</div>`)
      .join('');
  }
  
  const boardSizeFormulas = document.getElementById('board-size-formulas');
  if (boardSizeFormulas) {
    boardSizeFormulas.innerHTML = results.formulas.boardSizes
      .map(formula => `<div class="calculation-formula">${formula}</div>`)
      .join('');
  }
  
  const paperWeightFormulas = document.getElementById('paper-weight-formulas');
  if (paperWeightFormulas) {
    paperWeightFormulas.innerHTML = results.formulas.paperWeights
      .map(formula => `<div class="calculation-formula">${formula}</div>`)
      .join('');
  }
  
  const costFormulas = document.getElementById('cost-formulas');
  if (costFormulas) {
    costFormulas.innerHTML = results.formulas.costs
      .map(formula => `<div class="calculation-formula">${formula}</div>`)
      .join('');
  }
  
  // Update constants display
  document.getElementById('length-shrinkage-factor').textContent = results.constants.LENGTH_SHRINKAGE_FACTOR;
  document.getElementById('breadth-shrinkage-factor').textContent = results.constants.BREADTH_SHRINKAGE_FACTOR;
  document.getElementById('height-shrinkage-factor').textContent = results.constants.HEIGHT_SHRINKAGE_FACTOR;
  document.getElementById('flute-tuf').textContent = results.constants.FLUTE_TUF;
  document.getElementById('paper-cost-per-kg').textContent = results.constants.PAPER_COST_PER_KG;
  document.getElementById('labor-cost-percentage').textContent = (results.constants.LABOR_COST_PERCENTAGE * 100) + '%';
}