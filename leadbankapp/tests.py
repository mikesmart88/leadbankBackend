from django.test import TestCase
from .utils import get_exchange_rates
from .mailservice import send_mail

# Create your tests here.

send_mail(
                    "uzomamicheal07@gmail.com",
                    f"""
                        <section
  style="
    width: 100%;
    height: fit-content;
    background-color: whitesmoke;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Work Sans', sans-serif;
    padding: 20px 10px;
    box-sizing:border-box;
  "
>
  <div
    style="
      width: 100%;
      height: auto;
      background-color: white;
      overflow: hidden;
      border-radius: 10px;
    "
  >
    <div
      style="
        padding: 30px;
        background-image: url('https://leadbankuniversal.com/assets/bg_image-BumasGER.jpg');
        background-repeat: no-repeat;
        background-position: center;
        background-size: cover;
        display: flex;
        align-items: center;
        color: white;
        overflow: hidden;
        max-height: 100px;
      "
    >
      <div
        style="
          width: 30px;
          height: fit-content;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          box-sizing: border-box;

        "
      >
        <img
          src="https://leadbankuniversal.com/assets/leadbank-icon-BbymAn6i.png"
          alt="leadbank icon image"
          style="
          width:100%;
          height: auto;
          object-fit:cover;
          min-width:100%;
          max-width:100%;
          "
        />
      </div>
      <h2
        style="
          font-weight: 700;
          letter-spacing: -1px;
          margin: 0px;
          color:#333333
        "
      >
        Leadbank
      </h2>
    </div>

    <div style="padding: 20px; color:#333333; letter-spacing:-1px; line-height:150%;">
        <small style="margin:0 0 25px 0;font-size:14px;line-height:32px;color:#4B5563;">Hello Micheal</small>
        <h3>Welcome to Leadbank 😃</h3>
        <p style="margin:0 0 25px 0;font-size:14px;line-height:32px;color:#4B5563;">
  At LeadBank, we believe banking should be secure, simple, and accessible. Whether you're saving, transferring funds, managing multiple currencies, or growing your financial future, we're here to provide the tools you need every step of the way.
</p>
<p style="margin:0 0 25px 0;font-size:14px;line-height:34px;color:#4B5563;">
    Now, sit back as we relieve you of every hassle that comes with international transactions.
</p>
  </div>
  <br>
  <p style="margin:0 0 25px 0;font-size:13px;line-height:34px;color:#4B5563;text-align:center;">
    ©2026. Grey. All rights reserved.
  </p>
</section>

                    """,
                    "Welcome to Leadbank",
                    f"Micheal"
                )
