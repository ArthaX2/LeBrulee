from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from datetime import datetime, timedelta
import random

from app.extensions import db, mail
from app.forms.signUpForm import SignupForm
from app.models.users import User

main_bp = Blueprint("main", __name__)

# ------------------- DUMMY MENU -------------------
def get_menu_items():
    """Return menu items as dict keyed by ID for easy access."""
    return {
        1: {'id': 1, 'name': 'Butter Croissant', 'price': 3.50, 'img': 'https://parisbaguette.com/wp-content/uploads/2024/07/4217bea183204121b0c98bb193016ea3.jpg'},
        2: {'id': 2, 'name': 'French Baguette', 'price': 4.00, 'img': 'https://parisbaguette.com/wp-content/uploads/2024/07/10b8af2019c64896a35d7699a1dd283a-1.jpg'},
        3: {'id': 3, 'name': 'Sourdough Bread', 'price': 5.50, 'img': 'https://parisbaguette.com/wp-content/uploads/2024/09/0416af9e17fe404c9926750479f80b93.jpgautoformat2Ccompressq60cstinysrgbw1200h800fitfillfmpng32bgtransparents00119dbea559a42bf055e0dfeaddcc9e.jpg'},
        4: {'id': 4, 'name': 'Chocolate Croissant', 'price': 4.50, 'img': 'https://parisbaguette.com/wp-content/uploads/2024/07/eaccfb883f314dfdbe4855d42f224d35.jpg'},
        5: {'id': 5, 'name': 'New York Cheesecake', 'price': 6.50, 'img': 'https://parisbaguette.com/wp-content/uploads/2024/10/46e9b2052d204939b28ba2cf94b7746b.jpgautoformat2Ccompressq60cstinysrgbw1200h800fitfillfmpng32bgtransparents00355d9c16f902c68c9a7ea28beb936e.jpg'},
        6: {'id': 6, 'name': 'Chocolate Éclair', 'price': 4.00, 'img': 'https://parisbaguette.com/wp-content/uploads/2024/07/26c18267751e465994739368aca090f5.jpg'},
        7: {'id': 7, 'name': 'Crème Brûlée', 'price': 5.50, 'img': 'https://tse2.mm.bing.net/th/id/OIP.byUuF2LoFN0qcYKiBCEoYAHaEK?w=328&h=184&c=7&r=0&o=7&dpr=1.5&pid=1.7&rm=3'},
        8: {'id': 8, 'name': 'Macarons (6pc)', 'price': 12.00, 'img': 'https://parisbaguette.com/wp-content/uploads/2024/07/d9cf9583df534477b5b9f31ca57438b2.jpg'},
        9: {'id': 9, 'name': 'Espresso', 'price': 2.50, 'img': 'https://parisbaguette.com/wp-content/uploads/2024/07/79cca220c61843a4b653e56226a0f980-2.jpg'},
        10: {'id': 10, 'name': 'Cappuccino', 'price': 4.00, 'img': 'https://parisbaguette.com/wp-content/uploads/2024/07/a92b81da3d4d4378a5a25e638b0763da-2.jpg'},
        11: {'id': 11, 'name': 'Latte', 'price': 4.50, 'img': 'https://parisbaguette.com/wp-content/uploads/2024/07/ca4bbd77e36b436c90ad27907e6ff93e-13.jpg'},
        12: {'id': 12, 'name': 'Green Tea', 'price': 3.00, 'img': 'https://parisbaguette.com/wp-content/uploads/2024/07/1a0f96c51ec748ce9b4914f0725ac239-4.jpg'},
    }


def _get_cart_items():
    """Return a shallow copy of the cart stored in the session."""
    return list(session.get("cart", []))


def _save_cart_items(cart_items):
    session["cart"] = cart_items
    session.modified = True


def _calculate_totals(cart_items):
    total_amount = sum(item["price"] * item["quantity"] for item in cart_items)
    total_items = sum(item["quantity"] for item in cart_items)
    return round(total_amount, 2), total_items


def _get_order_history():
    return list(session.get("order_history", []))


def _save_order_history(order_history):
    session["order_history"] = order_history
    session.modified = True


def _next_order_id():
    order_id = session.get("order_counter", 1)
    session["order_counter"] = order_id + 1
    session.modified = True
    return order_id

# ------------------- BASIC PAGES -------------------
@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/about")
def about():
    return render_template("about.html")

@main_bp.route("/menu")
def menu():
    menu_data = get_menu_items()
    grouped_menu = {
        'pastries': [menu_data[i] for i in [1,2,3,4]],
        'cakes': [menu_data[i] for i in [5,6,7,8]],
        'beverages': [menu_data[i] for i in [9,10,11,12]]
    }
    cart_items = session.get("cart", [])
    return render_template("menu.html", grouped_menu=grouped_menu, cart_items=cart_items)

@main_bp.route("/store")
def store():
    return render_template("store.html")

@main_bp.route("/contact", methods=["GET","POST"])
def contact():
    if request.method=="POST":
        try:
            # Get form data
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            subject = request.form.get("subject", "").strip()
            message = request.form.get("message", "").strip()
            
            # Validate required fields
            if not all([name, email, subject, message]):
                flash("Please fill in all fields.", "error")
                return redirect(url_for("main.contact"))
            
            # Get recipient email from config
            recipient_email = current_app.config.get("CONTACT_EMAIL", "arthasuryapratama46@gmail.com")
            
            # Debug: Print mail configuration (remove in production)
            print("=" * 50)
            print("DEBUG: Mail Configuration")
            print(f"MAIL_SERVER: {current_app.config.get('MAIL_SERVER')}")
            print(f"MAIL_PORT: {current_app.config.get('MAIL_PORT')}")
            print(f"MAIL_USE_TLS: {current_app.config.get('MAIL_USE_TLS')}")
            print(f"MAIL_USERNAME: {current_app.config.get('MAIL_USERNAME')}")
            print(f"MAIL_PASSWORD: {'*' * len(str(current_app.config.get('MAIL_PASSWORD', '')))}")
            print(f"MAIL_DEFAULT_SENDER: {current_app.config.get('MAIL_DEFAULT_SENDER')}")
            print(f"Recipient: {recipient_email}")
            print("=" * 50)
            
            # Create email message
            msg = Message(
                subject=f"Contact Form: {subject}",
                recipients=[recipient_email],
                sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
                reply_to=email
            )
            
            # Email body with HTML formatting
            msg.body = f"""
New Contact Form Submission from LeBrulee Website

From: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
This email was sent from the LeBrulee contact form.
Reply directly to this email to respond to {name} ({email}).
"""
            
            # HTML version for better formatting
            msg.html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #0a1530, #152857); color: #fbbf24; padding: 20px; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
        .field {{ margin-bottom: 15px; }}
        .label {{ font-weight: bold; color: #0a1530; }}
        .value {{ margin-top: 5px; padding: 10px; background: white; border-left: 3px solid #fbbf24; }}
        .message-box {{ background: white; padding: 15px; border-left: 3px solid #0a1530; margin-top: 10px; }}
        .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2 style="margin: 0;">New Contact Form Submission</h2>
            <p style="margin: 5px 0 0 0;">LeBrulee Website</p>
        </div>
        <div class="content">
            <div class="field">
                <div class="label">From:</div>
                <div class="value">{name}</div>
            </div>
            <div class="field">
                <div class="label">Email:</div>
                <div class="value"><a href="mailto:{email}">{email}</a></div>
            </div>
            <div class="field">
                <div class="label">Subject:</div>
                <div class="value">{subject}</div>
            </div>
            <div class="field">
                <div class="label">Message:</div>
                <div class="message-box">{message.replace(chr(10), '<br>')}</div>
            </div>
        </div>
        <div class="footer">
            <p>This email was sent from the LeBrulee contact form.</p>
            <p>Reply directly to this email to respond to {name}.</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Send email
            print(f"Attempting to send email to {recipient_email}...")
            mail.send(msg)
            print("Email sent successfully!")
            flash("Thank you for your message! We'll get back to you soon.", "success")
            
        except Exception as e:
            # Log the error with full details
            import traceback
            error_details = traceback.format_exc()
            print("=" * 50)
            print("ERROR: Failed to send email")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print("\nFull Traceback:")
            print(error_details)
            print("=" * 50)
            flash(f"Sorry, there was an error sending your message: {str(e)}. Please try again later or contact us directly.", "error")
        
        return redirect(url_for("main.contact"))
    
    return render_template("contact.html")


@main_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.profile"))

    form = SignupForm()
    msg = ""

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            msg = "Username already taken. Please choose another."
        else:
            new_user = User(
                username=form.username.data,
                fullname=form.fullname.data,
                password=form.password.data,
            )
            db.session.add(new_user)
            db.session.commit()
            msg = "Account created successfully! Please log in."
    elif request.method == "POST":
        # Surface the first validation error for quick feedback.
        first_error_list = next(iter(form.errors.values()), [])
        msg = first_error_list[0] if first_error_list else "Please check the form inputs."

    return render_template("signup.html", form=form, msg=msg)


@main_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@main_bp.route("/cart")
def cart():
    cart_items = _get_cart_items()
    total_amount, _ = _calculate_totals(cart_items)
    return render_template("cart.html", cart_items=cart_items, total_amount=total_amount)


@main_bp.route("/cart/add", methods=["POST"])
def add_to_cart():
    payload = request.get_json(silent=True) or request.form
    if not payload:
        return jsonify({"success": False, "message": "No data provided."}), 400

    try:
        item_id = int(payload.get("item_id", 0))
    except (TypeError, ValueError):
        item_id = 0

    try:
        quantity = int(payload.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    quantity = max(1, quantity)
    is_update = str(payload.get("is_update", "")).lower() in {"true", "1", "yes"}

    menu_items = get_menu_items()
    menu_item = menu_items.get(item_id)
    if not menu_item:
        return jsonify({"success": False, "message": "Invalid menu item."}), 400

    cart_items = _get_cart_items()
    message = "Item added to cart."
    for item in cart_items:
        if item["id"] == item_id:
            if is_update:
                item["quantity"] = quantity
                message = "Cart updated."
            else:
                item["quantity"] += quantity
                message = "Item quantity updated."
            break
    else:
        cart_items.append({
            "id": menu_item["id"],
            "name": menu_item["name"],
            "price": float(menu_item["price"]),
            "img": menu_item["img"],
            "quantity": quantity,
        })

    _save_cart_items(cart_items)
    total_amount, total_items = _calculate_totals(cart_items)

    return jsonify({
        "success": True,
        "message": message,
        "cart_items": cart_items,
        "total_items": total_items,
        "total_amount": total_amount,
    })


@main_bp.route("/cart/remove", methods=["POST"])
def remove_from_cart():
    payload = request.get_json(silent=True) or request.form
    if not payload:
        return jsonify({"success": False, "message": "No data provided."}), 400

    try:
        item_id = int(payload.get("item_id", 0))
    except (TypeError, ValueError):
        item_id = 0

    cart_items = _get_cart_items()
    new_cart = [item for item in cart_items if item["id"] != item_id]

    if len(new_cart) == len(cart_items):
        return jsonify({"success": False, "message": "Item not found in cart."}), 404

    _save_cart_items(new_cart)
    total_amount, total_items = _calculate_totals(new_cart)

    return jsonify({
        "success": True,
        "message": "Item removed from cart.",
        "total_amount": total_amount,
        "total_items": total_items,
    })


@main_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_items = _get_cart_items()
    total_amount, total_items = _calculate_totals(cart_items)
    order_history = _get_order_history()
    recent_order_id = session.get("recent_order_id")
    recent_order = next((order for order in order_history if order["id"] == recent_order_id), None)

    if request.method == "POST":
        if not cart_items:
            flash("Your cart is empty. Please add items before checking out.", "error")
            return redirect(url_for("main.menu"))

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        payment_method = request.form.get("payment_method")

        if not all([name, email, address, payment_method]):
            flash("Please fill out all required fields and select a payment method.", "error")
            return redirect(url_for("main.checkout"))

        shipping_fee = 5.00
        delivery_minutes = random.randint(25, 45)
        delivery_eta = (datetime.utcnow() + timedelta(minutes=delivery_minutes)).strftime("%I:%M %p")
        order_id = _next_order_id()
        pretty_payment = "Cash on Delivery" if payment_method == "cod" else "Bank Transfer"

        new_order = {
            "id": order_id,
            "customer": name,
            "email": email,
            "address": address,
            "payment_method": pretty_payment,
            "status": "Preparing",
            "items": [{"name": item["name"], "quantity": item["quantity"], "price": item["price"]} for item in cart_items],
            "placed_at": datetime.utcnow().strftime("%b %d, %Y %I:%M %p"),
            "delivery_eta": delivery_eta,
            "delivery_minutes": delivery_minutes,
            "total": round(total_amount + shipping_fee, 2),
            "subtotal": total_amount,
            "shipping_fee": shipping_fee,
        }

        order_history.insert(0, new_order)
        _save_order_history(order_history)
        session["recent_order_id"] = order_id
        _save_cart_items([])

        flash("Order placed successfully! We are preparing your treats.", "success")
        return redirect(url_for("main.checkout"))

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total_amount=total_amount,
        total_items=total_items,
        order_history=order_history,
        recent_order=recent_order,
    )


@main_bp.route("/orders")
def orders():
    order_history = _get_order_history()
    return render_template("orders.html", order_history=order_history)


@main_bp.route("/orders/<int:order_id>/delivered", methods=["POST"])
def mark_order_delivered(order_id):
    order_history = _get_order_history()
    order = next((order for order in order_history if order["id"] == order_id), None)
    if not order:
        return jsonify({"success": False, "message": "Order not found."}), 404

    if order["status"] == "Delivered":
        return jsonify({"success": True, "message": "Order already delivered."})

    order["status"] = "Delivered"
    _save_order_history(order_history)
    return jsonify({"success": True, "message": "Order marked as delivered."})


@main_bp.route("/orders/<int:order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    order_history = _get_order_history()
    order = next((order for order in order_history if order["id"] == order_id), None)
    if not order:
        return jsonify({"success": False, "message": "Order not found."}), 404

    if order["status"] == "Cancelled":
        return jsonify({"success": True, "message": "Order already cancelled."})

    order["status"] = "Cancelled"
    _save_order_history(order_history)
    return jsonify({"success": True, "message": "Order cancelled."})


@main_bp.route("/orders/<int:order_id>/remove", methods=["POST"])
def remove_order(order_id):
    order_history = _get_order_history()
    new_history = [order for order in order_history if order["id"] != order_id]

    if len(new_history) == len(order_history):
        return jsonify({"success": False, "message": "Order not found."}), 404

    _save_order_history(new_history)
    if session.get("recent_order_id") == order_id:
        session.pop("recent_order_id")
    session.modified = True

    return jsonify({"success": True, "message": "Order removed from history."})
