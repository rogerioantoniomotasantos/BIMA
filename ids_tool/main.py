import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from datetime import date
import os
import re

# Function to sanitize XML element names
def sanitize_xml_tag(tag):
    # Replace invalid characters with underscores and ensure it starts with a letter or underscore
    tag = re.sub(r'[^a-zA-Z0-9_]', '_', tag)  # Replace non-alphanumeric chars with underscores
    if not re.match(r'^[a-zA-Z_]', tag):      # Ensure tag starts with a letter or underscore
        tag = '_' + tag
    return tag

# Function to generate IDS file
def generate_ids():
    namespaces = {
        'xs': "http://www.w3.org/2001/XMLSchema",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'ids': "http://standards.buildingsmart.org/IDS"
    }

    # Create root element with the appropriate namespaces
    ids = ET.Element('ids:ids', {
        'xmlns:ids': 'http://standards.buildingsmart.org/IDS',  # Define the IDS namespace
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',  # Define the xsi namespace
        'xsi:schemaLocation': 'http://standards.buildingsmart.org/IDS http://standards.buildingsmart.org/IDS/ids_09.xsd'  # Provide the schema location with the xsi prefix
    })

    # Add header metadata (ids:info)
    info = ET.SubElement(ids, 'ids:info')
    ET.SubElement(info, 'ids:title').text = description.get()
    ET.SubElement(info, 'ids:copyright').text = copyright.get()
    ET.SubElement(info, 'ids:version').text = "1.0"
    ET.SubElement(info, 'ids:description').text = "Description of the IDS document"
    ET.SubElement(info, 'ids:author').text = author.get()
    ET.SubElement(info, 'ids:date').text = str(date.today())
    ET.SubElement(info, 'ids:purpose').text = purpose.get()
    ET.SubElement(info, 'ids:milestone').text = milestone.get()

    # Add specifications (ids:specifications)
    specifications_elem = ET.SubElement(ids, 'ids:specifications')

    # Add each specification input
    for spec in specifications:
        specification_elem = ET.SubElement(specifications_elem, 'ids:specification', {
            'ifcVersion': 'IFC4',
            'name': 'Attribute conditions on entities',
            'identifier': '01',  # Example identifier
            'description': 'Describe why this condition is necessary.',
            'instructions': 'Provide guidelines for how this is to be described.'
        })

        # Add applicability (ids:applicability)
        applicability_elem = ET.SubElement(specification_elem, 'ids:applicability')
        entity_elem = ET.SubElement(applicability_elem, 'ids:entity')
        name_elem = ET.SubElement(entity_elem, 'ids:name')
        ET.SubElement(name_elem, 'ids:simpleValue').text = sanitize_xml_tag(spec['entity'].get())  # Using the stored variable

        # Add requirements (ids:requirements)
        requirements_elem = ET.SubElement(specification_elem, 'ids:requirements')

        for attr, value in spec['attributes'].items():
            attribute_elem = ET.SubElement(requirements_elem, 'ids:attribute')
            attr_name_elem = ET.SubElement(attribute_elem, 'ids:name')
            ET.SubElement(attr_name_elem, 'ids:simpleValue').text = sanitize_xml_tag(attr)

            value_elem = ET.SubElement(attribute_elem, 'ids:value')
            ET.SubElement(value_elem, 'ids:simpleValue').text = value.get()

    # Get current directory and file path
    output_path = os.path.join(os.getcwd(), "output_ids.xml")

    # Save as XML file
    tree = ET.ElementTree(ids)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    # Display file location in the status label
    status_label.config(text=f"IDS file created at {output_path}")

# Function to add a new specification section
def add_specification():
    frame = tk.Frame(root)
    frame.pack(pady=5, padx=10, fill='x')

    spec = {}

    # Use StringVar() to store the value of the entity
    entity_var = tk.StringVar()

    # Entity field (IFC class)
    entity_label = tk.Label(frame, text="Entity (IFC Class):")
    entity_label.pack(side=tk.LEFT)
    entity_entry = tk.Entry(frame, textvariable=entity_var)
    entity_entry.pack(side=tk.LEFT)
    spec['entity'] = entity_var  # Store the StringVar, not the Entry widget

    # Attributes
    attributes_frame = tk.Frame(frame)
    attributes_frame.pack(pady=5)

    def add_attribute():
        attr_frame = tk.Frame(attributes_frame)
        attr_frame.pack(pady=2, fill='x')

        attr_var = tk.StringVar()  # Store the attribute name
        value_var = tk.StringVar()  # Store the attribute value

        attr_label = tk.Entry(attr_frame, textvariable=attr_var)
        attr_label.pack(side=tk.LEFT, padx=5)
        value_entry = tk.Entry(attr_frame, textvariable=value_var)
        value_entry.pack(side=tk.LEFT, padx=5)

        spec['attributes'][attr_var.get()] = value_var  # Store the StringVars for both

    # Add initial attributes field
    add_button = tk.Button(frame, text="+ Add Attribute", command=add_attribute)
    add_button.pack()

    # Remove specification
    remove_button = tk.Button(frame, text="Remove Specification", command=frame.destroy)
    remove_button.pack(side=tk.RIGHT)

    # Store specification details
    spec['attributes'] = {}
    specifications.append(spec)

# Main GUI setup
root = tk.Tk()
root.title("IDS File Generator")

# Header information
header_frame = tk.Frame(root)
header_frame.pack(pady=10, padx=10, fill='x')

ifc_schema = tk.Entry(header_frame)
description = tk.Entry(header_frame)
author = tk.Entry(header_frame)
copyright = tk.Entry(header_frame)
purpose = tk.Entry(header_frame)
milestone = tk.Entry(header_frame)

tk.Label(header_frame, text="IFC Schema").pack(side=tk.LEFT)
ifc_schema.pack(side=tk.LEFT, padx=5)
tk.Label(header_frame, text="Description").pack(side=tk.LEFT)
description.pack(side=tk.LEFT, padx=5)
tk.Label(header_frame, text="Author").pack(side=tk.LEFT)
author.pack(side=tk.LEFT, padx=5)

# Specifications section
specifications = []
add_spec_button = tk.Button(root, text="+ Add Specification", command=add_specification)
add_spec_button.pack(pady=5)

# Generate IDS button
generate_button = tk.Button(root, text="Generate IDS", command=generate_ids)
generate_button.pack(pady=10)

# Status label
status_label = tk.Label(root, text="")
status_label.pack(pady=5)

# Start the GUI loop
root.mainloop()
