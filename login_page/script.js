function submit_pro_id() {
    var product_id=document.getElementById('product_id').value;
    if (product_id==="000000000000") {
        window.location.replace("https://www.washington.edu/");

    } else {
        alert("Wrong id, try it again! :(")
    }
}