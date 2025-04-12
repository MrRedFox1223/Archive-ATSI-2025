console.log("Working Fine");

const monthNames = ["Jan", "Feb", "Mar", "April", "May", "June",
    "July", "Aug", "Sept", "Oct", "Nov", "Dec"
];

$("#commentForm").submit(function (e) {
    e.preventDefault();

    let dt = new Date();
    let time = dt.getDay() + " " + monthNames[dt.getUTCMonth()] + ", " + dt.getFullYear()

    $.ajax({
        data: $(this).serialize(),

        method: $(this).attr("method"),

        url: $(this).attr("action"),

        dataType: "json",

        success: function (res) {
            console.log("Comment Saved to DB...");

            if (res.bool == true) {
                $("#review-res").html("Review added successfully.")
                $(".hide-comment-form").hide()
                $(".add-review").hide()

                let _html = '<div class="single-comment justify-content-between d-flex mb-30">'
                _html += '<div class="user justify-content-between d-flex">'
                _html += '<div class="thumb text-center">'
                //_html += '<img src="https://thumbs.dreamstime.com/b/default-avatar-profile-vector-user-profile-default-avatar-profile-vector-user-profile-profile-179376714.jpg" alt="" />'
                _html += '<a href="#" class="font-heading text-brand">' + res.context.user + '</a>'
                _html += '</div>'

                _html += '<div class="desc">'
                _html += '<div class="d-flex justify-content-between mb-10">'
                _html += '<div class="d-flex align-items-center">'
                _html += '<span class="font-xs text-muted">' + time + '&nbsp&nbsp </span>'
                _html += '</div>'

                for (var i = 1; i <= res.context.rating; i++) {
                    _html += '<i class="fas fa-star text-warning"></i>';
                }

                _html += '</div>'
                _html += '<p class="mb-10">' + res.context.review + '</p>'

                _html += '</div>'
                _html += '</div>'
                _html += ' </div>'

                $(".comment-list").prepend(_html)
            }
        }
    })
})

$(document).ready(function () {

    $(".add-to-cart-btn").on("click", function(){

            let this_val = $(this)
            let index = this_val.attr("data-index")
            let quantity = $(".product-quantity-" + index).val()
            let product_title = $(".product-title-" + index).val()
            let product_id = $(".product-id-" + index).val()
            let product_price = $(".current-product-price-" + index).text()
            let product_pid = $(".product-pid-" + index).val()
            let product_image = $(".product-image-" + index).val()

            console.log("Quantity:", quantity);
            console.log("Title:", product_title);
            console.log("Price:", product_price);
            console.log("ID:", product_id);
            console.log("PID:", product_pid);
            console.log("Image:", product_image);
            console.log("Index:", index);
            console.log("Currrent Element:", this_val);

        $.ajax({
                url: '/add-to-cart',
                data: {
                    'id': product_id,
                    'pid': product_pid,
                    'image': product_image,
                    'qty': quantity,
                    'title': product_title,
                    'price': product_price,
                },
                dataType: 'json',
                beforeSend: function () {
                    console.log("Adding Product to Cart...");
                },
                success: function (response) {
                    this_val.html("<i class='fas fa-check-circle'></i>")

                    console.log("Added Product to Cart!");
                    $(".cart-items-count").text(response.totalcartitems)


                }
            })
    })

    $(document).on("click", '.delete-product', function() {

            let product_id = $(this).attr("data-product")
            let this_val = $(this)

            console.log("Product ID:", product_id);

            $.ajax({
                url: "/delete-from-cart",
                data: {
                    "id": product_id
                },
                dataType: "json",
                beforeSend: function () {
                    this_val.hide()
                },
                success: function (response) {
                    this_val.show()
                    $(".cart-items-count").text(response.totalcartitems)
                    $("#cart-list").html(response.data)
                }
            })
        })

    $(document).on("click",'.update-product', function () {

        let product_id = $(this).attr("data-product")
        let this_val = $(this)
        let product_quantity = $(".product-qty-" + product_id).val()

        console.log("Product ID:", product_id);
        console.log("Product QTY:", product_quantity);

        $.ajax({
            url: "/update-cart",
            data: {
                "id": product_id,
                "qty": product_quantity,
            },
            dataType: "json",
            beforeSend: function () {
                this_val.hide()
            },
            success: function (response) {
                this_val.show()
                $(".cart-items-count").text(response.totalcartitems)
                $("#cart-list").html(response.data)
                window.location.reload()
            }
        })
    })

    $(document).on("click", ".make-default-address", function () {
        let id = $(this).attr("data-address-id")
        let this_val = $(this)

        console.log("ID is:", id);
        console.log("Element is:", this_val);

        $.ajax({
            url: "/make-default-address",
            data: {
                "id": id
            },
            dataType: "json",
            success: function (response) {
                console.log("Address Made Default....");
                if (response.boolean == true) {

                    $(".check").hide()
                    $(".action_btn").show()

                    $(".check" + id).show()
                    $(".button" + id).hide()

                }
            }
        })
    })
})