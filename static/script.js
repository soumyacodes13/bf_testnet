document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("order-form");
    const typeSelect = document.getElementById("type");
    const priceInput = document.getElementById("price");
    const sideSelect = document.getElementById("side");
    const submitBtn = document.getElementById("submit-btn");
    const btnText = submitBtn.querySelector(".btn-text");
    const spinner = submitBtn.querySelector(".spinner");
    const resultBox = document.getElementById("result-box");

    // Toggle price requirement based on order type
    typeSelect.addEventListener("change", (e) => {
        if (e.target.value === "LIMIT") {
            priceInput.required = true;
            priceInput.disabled = false;
        } else {
            priceInput.required = false;
            priceInput.disabled = true;
            priceInput.value = "";
        }
    });

    // Update color of side selector
    const updateSideColor = () => {
        if(sideSelect.value === "BUY") {
            sideSelect.style.color = "var(--buy-color)";
        } else {
            sideSelect.style.color = "var(--sell-color)";
        }
    };
    sideSelect.addEventListener("change", updateSideColor);
    updateSideColor(); // init

    // Handle form submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        // UI loading state
        submitBtn.disabled = true;
        btnText.classList.add("hidden");
        spinner.classList.remove("hidden");
        resultBox.classList.add("hidden");

        const payload = {
            symbol: document.getElementById("symbol").value,
            side: document.getElementById("side").value,
            type: document.getElementById("type").value,
            qty: document.getElementById("qty").value,
            price: document.getElementById("price").value || null
        };

        try {
            const response = await fetch("/api/order", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            
            resultBox.classList.remove("hidden", "success", "error");
            
            if (data.success) {
                const avgPrice = parseFloat(data.response.avgPrice);
                const reqPrice = data.request.price;
                const isLimit = data.request.type === "LIMIT";
                
                let priceText = "MARKET";
                if (avgPrice > 0) {
                    priceText = avgPrice.toFixed(2);
                } else if (isLimit && reqPrice) {
                    priceText = `Pending (Limit @ ${reqPrice.toFixed(2)})`;
                }

                resultBox.classList.add("success");
                resultBox.innerHTML = `
                    <strong>Success! Order Placed</strong><br>
                    Order ID: ${data.response.orderId}<br>
                    Status: ${data.response.status}<br>
                    Executed Qty: ${parseFloat(data.response.executedQty)} / ${data.request.quantity}<br>
                    Price: ${priceText}
                `;
            } else {
                resultBox.classList.add("error");
                resultBox.innerHTML = `
                    <strong>Failed to Place Order</strong><br>
                    ${data.error_type}: ${data.message}
                `;
            }
        } catch (err) {
            resultBox.classList.remove("hidden");
            resultBox.classList.add("error");
            resultBox.innerHTML = `<strong>Error</strong><br>Failed to connect to the server.`;
        } finally {
            // Restore UI state
            submitBtn.disabled = false;
            btnText.classList.remove("hidden");
            spinner.classList.add("hidden");
        }
    });
});
