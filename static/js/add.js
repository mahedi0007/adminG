const BASE_URL = "http://127.0.0.1:8000";

console.log('add.js loaded');
const formEl = document.getElementById("productForm");
if (!formEl) console.warn('productForm element not found');
else console.log('productForm element found');

formEl && formEl.addEventListener("submit", async function(e) {
    e.preventDefault();

    const productData = {
        name: document.getElementById("name").value,
        description: document.getElementById("description").value,
        price: parseFloat(document.getElementById("price").value),
        quantity: parseInt(document.getElementById("quantity").value),
        is_available: document.getElementById("is_available").checked,
        image_url: document.getElementById("image_url").value,
        category_id: parseInt(document.getElementById("category_id").value)
    };

    console.log('Submitting productData:', productData);
    try {
        const response = await fetch(`${BASE_URL}/products/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(productData)
        });

        const result = await response.json();

        if (!response.ok) {
            alert("Error: " + result.detail);
            return;
        }

        alert("Product added successfully!");
        console.log(result);

    } catch (error) {
        alert("Failed to add product");
        console.error(error);
    }
});
