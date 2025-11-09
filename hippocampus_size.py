import os
import io
import base64
import torch
import numpy as np
import streamlit as st
import pydicom
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from pymongo import MongoClient
from bson.binary import Binary
from show_patient import show_patient_form
from io import BytesIO
mpl.use("agg")
import torch.nn as nn

class UNet(nn.Module):
    def __init__(self, num_classes=3, in_channels=1, initial_filter_size=64, kernel_size=3, num_downs=4, norm_layer=nn.InstanceNorm2d):
        super(UNet, self).__init__()
        unet_block = UnetSkipConnectionBlock(in_channels=initial_filter_size * 2 ** (num_downs-1),
                                             out_channels=initial_filter_size * 2 ** num_downs,
                                             num_classes=num_classes, kernel_size=kernel_size,
                                             norm_layer=norm_layer, innermost=True)
        for i in range(1, num_downs):
            unet_block = UnetSkipConnectionBlock(in_channels=initial_filter_size * 2 ** (num_downs-(i+1)),
                                                 out_channels=initial_filter_size * 2 ** (num_downs-i),
                                                 num_classes=num_classes, kernel_size=kernel_size,
                                                 submodule=unet_block, norm_layer=norm_layer)
        unet_block = UnetSkipConnectionBlock(in_channels=in_channels, out_channels=initial_filter_size,
                                             num_classes=num_classes, kernel_size=kernel_size,
                                             submodule=unet_block, norm_layer=norm_layer,
                                             outermost=True)
        self.model = unet_block

    def forward(self, x):
        return self.model(x)

class UnetSkipConnectionBlock(nn.Module):
    def __init__(self, in_channels=None, out_channels=None, num_classes=1, kernel_size=3,
                 submodule=None, outermost=False, innermost=False, norm_layer=nn.InstanceNorm2d, use_dropout=False):
        super(UnetSkipConnectionBlock, self).__init__()
        self.outermost = outermost

        pool = nn.MaxPool2d(2, stride=2)
        conv1 = self.contract(in_channels, out_channels, kernel_size, norm_layer)
        conv2 = self.contract(out_channels, out_channels, kernel_size, norm_layer)
        conv3 = self.expand(out_channels * 2, out_channels, kernel_size)
        conv4 = self.expand(out_channels, out_channels, kernel_size)

        if outermost:
            final = nn.Conv2d(out_channels, num_classes, kernel_size=1)
            model = [conv1, conv2, submodule, conv3, conv4, final]
        elif innermost:
            upconv = nn.ConvTranspose2d(in_channels * 2, in_channels, kernel_size=2, stride=2)
            model = [pool, conv1, conv2, upconv]
        else:
            upconv = nn.ConvTranspose2d(in_channels * 2, in_channels, kernel_size=2, stride=2)
            model = [pool, conv1, conv2, submodule, conv3, conv4, upconv]
            if use_dropout:
                model.append(nn.Dropout(0.5))

        self.model = nn.Sequential(*model)

    def forward(self, x):
        if self.outermost:
            return self.model(x)
        else:
            crop = self.center_crop(self.model(x), x.size()[2], x.size()[3])
            return torch.cat([x, crop], 1)

    @staticmethod
    def contract(in_channels, out_channels, kernel_size=3, norm_layer=nn.InstanceNorm2d):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size, padding=1),
            norm_layer(out_channels),
            nn.LeakyReLU(inplace=True)
        )

    @staticmethod
    def expand(in_channels, out_channels, kernel_size=3):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size, padding=1),
            nn.LeakyReLU(inplace=True)
        )

    @staticmethod
    def center_crop(layer, target_width, target_height):
        batch_size, n_channels, layer_width, layer_height = layer.size()
        xy1 = (layer_width - target_width) // 2
        xy2 = (layer_height - target_height) // 2
        return layer[:, :, xy1:(xy1 + target_width), xy2:(xy2 + target_height)]

class UNetInferenceAgent:
    def __init__(self, parameter_file_path='', model=None, device="cpu", patch_size=64):
        self.model = model or UNet(num_classes=3)
        self.patch_size = patch_size
        self.device = device
        if parameter_file_path:
            self.model.load_state_dict(torch.load(parameter_file_path, map_location=self.device))
        self.model.to(device)

    def single_volume_inference_unpadded(self, volume):
        volume = med_reshape(volume, (volume.shape[0], self.patch_size, self.patch_size))
        return self.single_volume_inference(volume)

    def single_volume_inference(self, volume):
        self.model.eval()
        slices = np.zeros(volume.shape)
        with torch.no_grad():
            for i, slice_img in enumerate(volume):
                slice_tensor = torch.from_numpy(slice_img).float().unsqueeze(0).unsqueeze(0).to(self.device)
                pred = self.model(slice_tensor)
                pred = np.squeeze(pred.cpu().detach())
                slices[i, :, :] = torch.argmax(pred, dim=0)
        return slices

def med_reshape(image, new_shape):
    reshaped_image = np.zeros(new_shape)
    x, y, z = image.shape
    reshaped_image[:x, :y, :z] = image
    return reshaped_image

def load_dicom_volume_as_numpy_from_list(dcmlist):
    slices = [np.flip(dcm.pixel_array).T for dcm in sorted(dcmlist, key=lambda dcm: dcm.InstanceNumber)]
    hdr = dcmlist[0]
    hdr.PixelData = None
    return (np.stack(slices, axis=2), hdr)

def get_predicted_volumes(pred):
    anterior_vol = np.sum(pred == 1)
    posterior_vol = np.sum(pred == 2)
    total_vol = anterior_vol + posterior_vol
    return {"anterior": anterior_vol, "posterior": posterior_vol, "total": total_vol}

def add_background(image_path: str):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def show_Size():
    st.set_page_config(page_title="HippoVolume.AI", layout="wide")
    st.markdown(
        """
        <div style="
            background-color: #f0f8ff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border-left: 6px solid #1f77b4;">
            <h2 style="color: #1f77b4; margin: 0; text-align: center;">🧠 Calculate Hippocampus Size</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    add_background("Image/12.jpg")
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="data:image/gif;base64,%s" width="600">
        </div>
        """ % base64.b64encode(open("Image\\Hippocampus.gif", "rb").read()).decode(),
        unsafe_allow_html=True
    )


    uploaded_files = st.file_uploader(
        "Upload DICOM Series Files (.dcm only)", 
        accept_multiple_files=True,
        type=["dcm"] 
    )

    if uploaded_files:
        dicoms = []
        for file in uploaded_files:
            try:
                dcm = pydicom.dcmread(file)
                if hasattr(dcm, 'SeriesDescription') and dcm.SeriesDescription == 'HippoCrop':
                    dicoms.append(dcm)
            except Exception as e:
                st.warning(f"⚠️ Error reading file: {file.name}")

        if len(dicoms) == 0:
            st.error("❌ No valid 'HippoCrop' series found in uploaded files.")
        else:
            volume, header = load_dicom_volume_as_numpy_from_list(dicoms)

            inference_agent = UNetInferenceAgent(
                device="cpu",
                parameter_file_path="model.pth"
            )

            pred_label = inference_agent.single_volume_inference_unpadded(volume)
            pred_volumes = get_predicted_volumes(pred_label)

            st.write(f"**Anterior Volume:** {pred_volumes['anterior']}")
            st.write(f"**Posterior Volume:** {pred_volumes['posterior']}")
            st.write(f"**Total Volume:** {pred_volumes['total']}")

            middle_slice_index = volume.shape[2] // 2
            middle_slice = np.flip((volume[:, :, middle_slice_index] / np.max(volume)) * 255).T.astype(np.uint8)
            st.image(middle_slice, caption="Middle Slice of the Hippocampus", clamp=True)

            final_class = "Demented"

            hippocampus_sizes = {
                final_class: {
                    "Left": pred_volumes["anterior"],
                    "Right": pred_volumes["posterior"],
                    "Total": pred_volumes["total"]
                }
            }

            processed_images = [middle_slice]

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Back to Patient Information Form", key="logout_btn"):
                    st.session_state["current_page"] = "patient_form"
                    st.session_state["patient_form_submitted"] = False
                    st.rerun()

            with col2:
                if st.button("Generate Report", key="report_btn"):
                    patient_id = st.session_state.get("patient_id", "123")
                    full_name = st.session_state.get("full_name", "John Doe")
                    gender = st.session_state.get("gender", "Male")
                    age = st.session_state.get("age", "70")
                    blood_group = st.session_state.get("blood_group", "O+")
                    contact = st.session_state.get("contact", "0000")
                    email = st.session_state.get("email", "email@example.com")
                    hippo = hippocampus_sizes.get(final_class)

                    buffer = BytesIO()
                    c = canvas.Canvas(buffer, pagesize=letter)
                    width, height = letter
                    center_x = width / 2

                    c.setFont("Helvetica-Bold", 20)
                    c.setFillColor(colors.darkblue)
                    c.drawCentredString(center_x, height - 40, "Quantification Alzheimer Disease Progression")

                    c.setFont("Helvetica", 10)
                    c.setFillColor(colors.black)
                    c.drawCentredString(center_x, height - 60, "Project Number # 51.")
                    c.drawCentredString(center_x, height - 75, "Sir Syed University of Engineering and Technology")
                    c.drawCentredString(center_x, height - 90, "Phone: +92 315 5974603 | Email: se21f-018@suet.edu.pk")

                    c.setFont("Helvetica-Bold", 16)
                    c.setFillColor(colors.green)
                    c.drawCentredString(center_x, height - 120, "ALZHEIMER MRI SCAN REPORT (Hippocampus Size)")

                    c.setFont("Helvetica-Bold", 14)
                    c.setFillColor(colors.darkred)
                    c.drawString(30, height - 150, "Patient Information:")
                    c.setFont("Helvetica", 11)
                    c.setFillColor(colors.black)
                    c.drawString(30, height - 170, f"Patient ID: {patient_id}")
                    c.drawString(400, height - 170, f"Full Name: {full_name}")
                    c.drawString(30, height - 190, f"Gender: {gender}")
                    c.drawString(400, height - 190, f"Age: {age}")
                    c.drawString(30, height - 210, f"Blood Group: {blood_group}")
                    c.drawString(400, height - 210, f"Contact: {contact}")
                    c.drawString(30, height - 230, f"Email: {email}")

                    if hippo:
                        c.drawString(30, height - 260, "Hippocampus Size:")
                        c.drawString(30, height - 290, f"Left: {hippo['Left']}")
                        c.drawString(250, height - 290, f"Right: {hippo['Right']}")
                        c.drawString(470, height - 290, f"Total: {hippo['Total']}")

                    y_offset = height - 480
                    for idx, img in enumerate(processed_images[:3]):
                        image_pil = Image.fromarray(img)
                        image_path = f"temp_img_{idx}.png"
                        image_pil.save(image_path)
                        c.drawImage(image_path, 30, y_offset, width=200, height=150)
                        y_offset -= 160
                        os.remove(image_path)

                    c.save()
                    buffer.seek(0)

                    hippo = {k: int(v) for k, v in hippo.items()}
                    pdf_binary = Binary(buffer.getvalue())
                    report_doc = {
                        "patient_id": patient_id,
                        "name": full_name,
                        "age": age,
                        "gender": gender,
                        "blood_group": blood_group,
                        "contact": contact,
                        "email": email,
                        "class": final_class,
                        "volumes": hippo,
                        "report_pdf": pdf_binary,
                    }

                    client = MongoClient("mongodb://localhost:27017")
                    db = client["MRI_Scan"]
                    db["Reports"].insert_one(report_doc)

                    b64_pdf = base64.b64encode(buffer.getvalue()).decode("utf-8")
                    link = f'<a href="data:application/pdf;base64,{b64_pdf}" download="alzheimer_report.pdf">📄 Download Report</a>'
                    st.markdown(link, unsafe_allow_html=True)