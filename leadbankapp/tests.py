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
          color:#ffffff
        "
      >
        Leadbank
      </h2>
    </div>

    <div style="padding: 20px; color:#333333; letter-spacing:-0.5px; line-height:150%;">
        <small style="margin:0 0 25px 0;font-size:14px;line-height:32px;color:#4B5563;">Hello Micheal</small>
        <h3>Your wallet has been funded successfully! 🤑</h3>
        <p style="margin:0 0 25px 0;font-size:14px;line-height:32px;color:#4B5563;">
  Your details are shown below:
<br>
<table style="width: 100%; background-color: #bebebe67; border-radius: 10px; border-spacing:0px">
  <tr style="align-items:center; justify-content:space-between; width:100%;">
    <th style="padding: 10px 15px; text-align:left; width: 50%;border-bottom:1px solid #f5f5f5;  font-weight:500; font-size: 14px; line-height:32px; color:#4B5563;">Transaction Type</th>
     <td style="padding: 10px 15px; text-align:left; border-bottom:1px solid #f8f8f8; width: 50%;font-size: 14px; line-height:32px; color:#4B5563;" >Depoiste</td>
  </tr>
  <tr style="align-items:center; justify-content:space-between; width:100%;">
    <th style="padding: 10px 15px; text-align:left; width: 50%;border-bottom:1px solid #f5f5f5;  font-weight:500; font-size: 14px; line-height:32px; color:#4B5563;">Amount</th>
     <td style="padding: 10px 15px; text-align:left; border-bottom:1px solid #f8f8f8; width: 50%;font-size: 14px; line-height:32px; color:#4B5563;" >$1,000.00</td>
  </tr>
  <tr style="align-items:center; justify-content:space-between; width:100%;">
    <th style="padding: 10px 15px; text-align:left; width: 50%;border-bottom:1px solid #f5f5f5;  font-weight:500; font-size: 14px; line-height:32px; color:#4B5563;">Description</th>
     <td style="padding: 10px 15px; text-align:left; border-bottom:1px solid #f8f8f8; width: 50%;font-size: 14px; line-height:32px; color:#4B5563;" >Sent to Uzoma micheal</td>
  </tr>
  <tr style="align-items:center; justify-content:space-between; width:100%;">
    <th style="padding: 10px 15px; text-align:left; width: 50%;border-bottom:1px solid #f5f5f5;  font-weight:500; font-size: 14px; line-height:32px; color:#4B5563;">Refrence</th>
     <td style="padding: 10px 15px; text-align:left; border-bottom:1px solid #f8f8f8; width: 50%;font-size: 14px; line-height:32px; color:#4B5563;" >#14</td>
  </tr>
  <tr style="align-items:center; justify-content:space-between; width:100%;">
    <th style="padding: 10px 15px; text-align:left; width: 50%;border-bottom:1px solid #f5f5f5;  font-weight:500; font-size: 14px; line-height:32px; color:#4B5563;">Date & Time</th>
     <td style="padding: 10px 15px; text-align:left; border-bottom:1px solid #f8f8f8; width: 50%;font-size: 14px; line-height:32px; color:#4B5563;" >12-4-25 T 12:59pm</td>
  </tr>
</table>

<p style="margin:0 0 25px 0;font-size:14px;line-height:32px;color:#4B5563;">
  If you didn't initiate this transaction, please contact our support team immediately, by sending an email to
  <br>
  <a style="color: #000;" href="mailto:support@leadbankuniversal.com">
    support@leadbankuniversal.com
  </a>
</p>

  </div>
  <br>
  <p style="margin:0 0 25px 0;font-size:13px;line-height:34px;color:#4B5563;text-align:center;">
    ©2026. Grey. All rights reserved.
  </p>
</section>
                    """,
                    "Welcome to Leadbank",
                    f"Micheal",
                )
