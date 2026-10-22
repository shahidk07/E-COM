/* ===== PLACE ORDER ===== */
const placeOrderBtn = document.getElementById("place-order-btn");
const addressForm = document.getElementById("address-form");
let addressId;

placeOrderBtn.addEventListener("click", () => {
    if (!addressForm.checkValidity() && !addressId) {
        addressForm.reportValidity();
        return;
    }
    placeOrder();
});

async function placeOrder() {
    const selectedAddress = document.querySelector('input[name="saved_address"]:checked');
    let formData;
    if (selectedAddress) {
        addressId = selectedAddress.value;
        formData = new FormData();
        formData.append("address_id", addressId);
    } else {
        formData = new FormData(addressForm);
    }

    const paymentMethod = document.querySelector('input[name="payment_method"]:checked').value;
    formData.append("payment_method", paymentMethod);

    for (const [key, value] of formData.entries()) {
        console.log(key, value);
    }

    const response = await fetch("/place_order/", {
        method: "POST",
        headers: { "X-CSRFToken": "{{ csrf_token }}" },
        body: formData
    });

    const result = await response.json();
    console.log("SERVER RESPONSE:", result);
    if (result.status == 200) {
        showOrderSuccess();
        setTimeout(() => { window.location.href = "/orders/"; }, 2000);
    }
}

function showOrderSuccess() {
    document.getElementById("orderSuccessModal").classList.add("vis");
}


/* ===== ADDRESS TOGGLING ===== */
const addAddressCard = document.getElementById("add-address-card");
const savedSection = document.getElementById("saved-addresses-section");
const shipSection = document.getElementById("shipping-section");
const backBtn = document.getElementById("back-to-saved-btn");

if (addAddressCard) {
    addAddressCard.addEventListener("click", () => {
        addressId = null;
        add_address_card.classList.add("hidden");
        savedSection.classList.add("hidden");
        shipSection.classList.remove("hidden");
    });
}
if (backBtn) {
    backBtn.addEventListener("click", () => {
        shipSection.classList.add("hidden");
        savedSection.classList.remove("hidden");
    });
}


/* ===== SAVED ADDRESS SELECTION ===== */
const savedRadios = document.querySelectorAll('input[name="saved_address"]');
const addrCards = document.querySelectorAll('.addr-card');

savedRadios.forEach(radio => {
    radio.addEventListener("change", () => {
        addressId = radio.value;
        addrCards.forEach(c => c.classList.remove('sel'));
        radio.closest('.addr-card').classList.add('sel');
    });
});

addrCards.forEach(card => {
    card.addEventListener('click', e => {
        if (e.target.closest('.addr-acts')) return;
        const r = card.querySelector('.addr-radio');
        r.checked = true;
        r.dispatchEvent(new Event('change'));
    });
});

/* ===== EDIT / DELETE ADDRESS ===== */
const delBtns=document.getElementsByClassName("btn-del");
// const editBtns=document.getElementsByClassName("btn-edit");

for (const delBtn of delBtns){
    delBtn.addEventListener("click",async()=>{
    var addressId=delBtn.dataset.addressId;
    console.log("Deleting address with address id",addressId);
    const response=await fetch("/delete_address/",{
        method:"DELETE",
        headers:{"X-CSRFToken":"{{csrf_token }}"},
        body:JSON.stringify({"address_id":addressId})
    })
    const result=await response.json();
    console.log(result.message);
    console.log(result.status);
     if (response.ok) {
            
        //delBtn.closest(".address-card") means  tarting from the clicked Delete button, find the nearest parent element having the class .address-card.
            const addressCard = delBtn.closest(".addr-card");

            addressCard.remove();
        }
});
}



const editButtons = document.querySelectorAll(".edit-address");

   ////////// HTTP REQUEST FOR EDIT ADDRESS/////////// 
    async function updateAddress() {
    const formData = new FormData(addressForm);
    formData.append("address_id", addressId);

    try {
        const response = await fetch("/update_address/", {
            method: "POST",
            headers: {
                "X-CSRFToken": "{{ csrf_token }}"
            },
            body: formData
        });

        const result = await response.json();
        console.log("SERVER RESPONSE:", result);

        if (response.ok && result.success) {
            alert("Address updated successfully!");
            window.location.reload();
        } else {
            alert(result.message || "Failed to update address.");
        }
    } catch (error) {
        console.error("Error updating address:", error);
        alert("Something went wrong. Please try again.");
    }
}

editButtons.forEach((editBtn) => {
    editBtn.addEventListener("click", () => {
        // Find the address card that contains this button
        const addressCard = editBtn.closest(".addr-card");

        // Collect the address data
        const address = addressCard.dataset;
        addressId = address.addressId;
        console.log(address); // Check all address data

        // Populate the existing form
        document.getElementById("full-name").value = address.fullName;
        document.getElementById("phone-number").value = address.phone;
        document.getElementById("address-line-1").value = address.addressLine1;
        document.getElementById("address-line-2").value = address.addressLine2;
        document.getElementById("city").value = address.city;
        document.getElementById("state").value = address.state;
        document.getElementById("pincode").value = address.pincode;
    
        // Debugging
        console.log("Editing address:", address.addressId);

        // Hide the saved addresses and Add New Address card
        const add_address_card = document.getElementById("add-address-card");
        const saved_addresses_section = document.getElementById("saved-addresses-section");
        const add_address_form = document.getElementById("shipping-section");
        saved_addresses_section.classList.add("hidden");
        add_address_card.classList.add("hidden");

        // Show the address form
        add_address_form.classList.remove("hidden");

        document.querySelector("#shipping-section .sec-title").textContent = "Edit Address";
        document.getElementById("save-address-btn").textContent = "Save Changes";
    
    
    });
    });

    document.getElementById("address-form").addEventListener("submit", (event) => {
    event.preventDefault();

    if (addressId) {
        updateAddress();
    }
});







/* ===== PAYMENT SELECTION ===== */
const payRadios = document.querySelectorAll('input[name="payment_method"]');
const payOpts = document.querySelectorAll('.pay-opt');

payRadios.forEach(radio => {
    radio.addEventListener("change", () => {
        payOpts.forEach(o => o.classList.remove('sel'));
        radio.closest('.pay-opt').classList.add('sel');
    });
});