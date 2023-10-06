from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.prompts.chat import SystemMessage

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field



#################### pydantic output prompt

class Table(BaseModel):
  Name: list[str] = Field(description='Retrieve the key.')
  Value : list[str]|None = Field(description="Retrieve the value corresponding to the key as String Format.")

class QA(BaseModel):
  Name: str = Field(description="{question}")
  Reference: str = Field(description="the extracted source exclusively from source file in the metadata which retrieved, not from the document content. If no reference is available, use '-'.")
  Specification: Table|str = Field(description="the answer to the user's {question}")

parser = PydanticOutputParser(pydantic_object=QA)
format_instructions = parser.get_format_instructions()

#################### basic prompt

#System Prompt
system_template = """You are an expert in the Steel industry. Use only given information.
Kindly examine the Given Steel Order document and address the following questions.\n:"""

#Human Prompt
human_template = """
Q : Based on the provided document, What is requested about ```{question}``` in this document?
Further description about the {question} are as follows:

description : ```{description}```

{format_instructions}

"""

system_message = SystemMessage(
  content= (system_template)
)
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

combined_prompt = ChatPromptTemplate.from_messages([
    system_message,
    human_message_prompt
    ])

#################### question sheet

qr_dic = {'Immersion UT': 'Definition: Ultrasonic testing where the material is submerged in a fluid to find defects using a 2D C-SCAN image. Synonyms: Immersion Ultrasonic Testing, Macro Inclusion Inspection. Unit: ',
 'Twist': "Definition: A deformation showing a spiraling action around a material's longitudinal axis, indicative of structural flaws. Synonyms: Spiral deformation. Unit: degree(˚)",
 'Corner Radius, Corner R': 'Definition: The rounded corner where two surfaces meet on a product. Synonyms: Edge radius. Unit: R, mm',
 'Chamfer': 'Definition: Creating a symmetrical sloping surface at an edge or corner. Synonyms: Unit: C, mm',
 'Burr': 'Definition: A rough edge formed on steel post-cutting, which is often removed to maintain functionality. Synonyms: Rough ridge Unit: mm',
 'Squareness': 'Definition: Post-cutting inspection to identify irregularities. Synonyms: Post-cutting inspection. Cutting Surface Inspection Unit: degree(˚), mm',
 'Bending Test': "Definition: A test to evaluate a material's behavior under bending forces. Synonyms: Flexural test. Unit: ",
 'Chemical Composition': 'Definition: Identifying elements and compounds in a material, essential for adhering to industry standards. Synonyms: Elemental composition. Unit: wt% (weight percent)',
 'Ideal Diameter': 'Definition: Calculated value based on chemical composition ratio, used in steel product assessment. Synonyms: Ideal Critical Diameter, ID, DI. Unit: -',
 'Decarburization': "Definition: Reduction of carbon content in steel's surface; measures the layer depth in mm or percentage of diameter. Synonyms: Total Decarburization, Decarburized Layer. Unit: mm",
 'Gas': 'Definition: Chemical element measurement in parts per million (ppm). Synonyms: Gas Analysis, Oxygen, Hydrogen. Nitrogen, N2, H2, O2, Unit: ppm, wt%, -',
 'Grain Size': 'Definition: Indicates material properties by measuring individual crystal size. Synonyms: Austenite grain size, AGS, Unit : -, No., Number, ASTM No.',
 'Hardness': 'Definition: Measured in HRB, HRC, HB range. Synonyms: Rockwell hardness, Brinell hardness, Vickers hardness. Surface hardness Unit: HB, HBW, HRC, HRB, HV, HS',
 'Heat Treatment': 'Definition: Enhances metal properties through controlled heating and cooling. Cooling parameter, media : Water, Air cooling, Oil Synonyms: 아래 내용 참조  - N (Normalizing), Q (Quenching), T (Tempering), A (Annealing), LA (Low Annealing), FA (Full Annealing), SA (Soft Annealing or Spheroidizing Annealing), SRA (Stress Relief Annealing) Unit: temperature(℃, ℉), time(min, hr)',
 'Impact Test': "Definition: Assesses material's resistance to sudden loads. Synonyms: Charpy Test, Charpy Impact Test, Unit: J, J/cm², ft-lbs, kgf-m/cm²",
 'Jominy Test': 'Definition: Evaluates metal hardenability post-quenching according to distance (mm or inch). Synonyms:Hardenability, Jominy, Unit: HRC',
 'Macro Structure': "Definition: Defines material's large-scale structural elements. Synonyms: Unit: -",
 'Macro-Streak-Flaw Test': 'Definition: Measures the quality and uniformity by assessing the internal flaws present. Synonyms: Unit: mm',
 'Diameter': 'Definition: Refers to the outer dimension of materials or products. Synonyms: Size. Unit: mm, inch',
 'Size Tolerance': 'Definition: Specifies allowable variations in size. Synonyms:  Unit: mm, inch, %',
 'Length': 'Definition: Refers to the overall measurement of a steel bar or product. Synonyms: Bar Length, Product Length. Unit: mm, inch',
 'Length Tolerance': 'Definition: Indicates allowable deviation from the specified length. Synonyms:  Unit: mm, inch',
 'Out of Round': 'Definition: Refers to any deviation from a perfectly round shape in cross-section. Synonyms: Out of Square, Unit: mm, inch, %',
 'Reduction Ratio': 'Definition: Ratio depicting the level of deformation in steel production, calculated from the initial and final cross-sectional areas. Synonyms: Rolling Ratio, Forging Ratio Unit:',
 'Micro Structure': "Definition: Refers to the microscopic characteristics of steel's grains influencing its properties Synonyms:  Unit:",
 'Non-Metallic Inclusion': 'Definition: Concerns the non-metallic impurities in steel affecting its mechanical attributes; involves assessing microscopic inclusions. Synonyms:  Unit:',
 'Residual Magnetism': 'Definition: Magnetism remaining in steel post removing an external magnetic field. Synonyms: Remanent Magnetism. Unit: Tesla (T), Gauss (G), Oersted (Oe), A/m',
 'Segregation Test': 'Definition: A test to determine how severe the segregation of components is inside the material. Synonyms: Unit:',
 'Spark Test': 'Definition: Qualitative test distinguishing steel types based on spark pattern and color produced when in contact. Synonyms: Unit:',
 'Straightness': 'Definition: The measure of deviation from straightness in steel products affecting processing and application Synonyms: Alignment, Banding Unit: mm/m, mm',
 'Surface Defect': 'Definition: Irregularities and imperfections on steel surfaces affecting performance. Synonyms: Surface Flaw. Unit: mm, %',
 'Al/N ratio': 'Definition: The aluminum to nitrogen ratio in steel composition. Synonyms:  Unit: ',
 'Macro Inclusions': 'Definition: Involves large non-metallic inclusions in steel, analyzed for determining steel quality and mechanical attributes. Synonyms: Unit:',
 'Ultrasonic Test': 'Definition: Non-destructive technique assessing the hardened layer depth in materials; complies with standards like EN 10308. Synonyms: UT, US Test Unit: mm'}