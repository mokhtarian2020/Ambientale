# HealthTrace - User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [User Roles](#user-roles)
3. [System Access](#system-access)
4. [Disease Reporting](#disease-reporting)
5. [Patient Management](#patient-management)
6. [Epidemiological Investigations](#epidemiological-investigations)
7. [Dashboard and Analytics](#dashboard-and-analytics)
8. [Environmental Data](#environmental-data)
9. [Troubleshooting](#troubleshooting)

## Getting Started

### System Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Login credentials provided by system administrator

### First Login
1. Navigate to the HealthTrace URL provided by your administrator
2. Enter your username and password
3. Click "Accedi" (Login)
4. You will be redirected to the main dashboard

## User Roles

HealthTrace supports four main user roles:

### MMG (Medici di Medicina Generale) - General Practitioners
**Permissions:**
- Report infectious diseases
- Search and view patients
- Update patient information
- Change patient disease status

### PLS (Pediatri di Libera Scelta) - Pediatricians of Free Choice
**Permissions:**
- Report infectious diseases (pediatric patients)
- Search and view patients
- Update patient information
- Change patient disease status

### U.O.S.D. (Unità Operativa Semplice Dipartimentale)
**Permissions:**
- All MMG/PLS permissions
- Conduct epidemiological investigations
- Access specialized disease investigation forms
- Contact tracing

### U.O.C. Epidemiologia (Unità Operativa Complessa - Epidemiologia)
**Permissions:**
- All system features
- View all dashboards and analytics
- Access environmental correlation data
- Generate reports and statistics
- Geo-visualization capabilities

## System Access (CU04)

### Login Process
1. **Access URL**: Open your web browser and navigate to the HealthTrace system
2. **Enter Credentials**: 
   - Username: Your assigned username
   - Password: Your assigned password
3. **Authentication**: Click "Accedi" (Login)
4. **Dashboard**: Upon successful login, you'll see the main dashboard

### Home Page Features
After login, you'll see:
- Navigation menu on the left
- Main content area with dashboard widgets
- User information in the top right corner
- Logout option

## Disease Reporting

### CU05: Infectious Disease Reporting

#### Creating a New Report
1. **Navigate**: Click "Segnalazioni" (Reports) in the left menu
2. **New Report**: Click "Nuova Segnalazione" (New Report)
3. **Fill Form**: Complete all required fields:

##### Disease Information
- **Malattia Infettiva** (Infectious Disease): Select from dropdown
- **Diagnosi U.O.S.D.** (UOSD Diagnosis): Enter diagnosis details

##### Patient Personal Data
- **Codice Fiscale/STP/ENI**: Enter patient identification
- **Cognome** (Surname): Patient's last name
- **Nome** (Name): Patient's first name
- **Sesso** (Gender): Select Male/Female/Other
- **Data di Nascita** (Birth Date): Select date
- **Luogo di Nascita** (Place of Birth): Country, Province, Municipality

##### Additional Information
- **Professione** (Profession): Patient's occupation
- **Indirizzo di Residenza** (Residence Address): Full address
- **Contatto Telefonico** (Phone Contact): Contact number

##### Clinical Data
- **Data Insorgenza Sintomi** (Symptom Onset Date): When symptoms started
- **Comune Insorgenza** (Onset Municipality): Where symptoms began
- **Ricovero** (Hospitalization): Yes/No
- **Stato Vaccinale** (Vaccination Status): Vaccinated/Unvaccinated/Unknown
- **Numero Dosi** (Number of Doses): If vaccinated
- **Data Ultima Dose** (Last Dose Date): If applicable
- **Tipo Vaccino** (Vaccine Type): Vaccine name

##### Reporting Information
- **Medico Segnalante** (Reporting Doctor): Your name (auto-filled)
- **Contatto Telefonico** (Phone Contact): Your contact number
- **Data Segnalazione** (Report Date): Today's date (auto-filled)

4. **Save**: Click "Salva Segnalazione" (Save Report)

## Patient Management

### CU06: Patient Research
1. **Navigate**: Go to "Pazienti" (Patients) section
2. **Search Options**:
   - **Nome** (Name): Enter patient's first name
   - **Cognome** (Surname): Enter patient's last name
   - **Codice Fiscale** (Tax Code): Enter full or partial tax code
3. **Search**: Click "Cerca" (Search)
4. **Results**: View search results in the table below

### CU07: View Patient
1. **From Search Results**: Click on any patient name in search results
2. **Patient Card Opens**: Shows complete patient information:
   - Personal data
   - Contact information
   - Medical history
   - Disease reports
   - Investigation records

### CU08: Patient Change
1. **Open Patient Card**: Navigate to patient as described above
2. **Edit Mode**: Click "Modifica" (Edit) button
3. **Update Information**: Change any editable fields
4. **Status Change**: Update patient status:
   - **Attivo** (Active) - Red light indicator
   - **Guarito** (Recovered) - Green light indicator
   - **Deceduto** (Deceased) - Black light indicator
5. **Save Changes**: Click "Salva Modifiche" (Save Changes)

### CU09: Research by Infectious Disease
1. **Navigate**: Go to "Malattie" (Diseases) section
2. **Disease Filter**: Select specific disease from dropdown
3. **Search**: Click "Cerca per Malattia" (Search by Disease)
4. **Patient List**: View all patients with selected disease
5. **Patient Details**: Click on any patient to open their card

## Epidemiological Investigations

### CU10: Epidemiological Investigation
*Available to U.O.S.D. and U.O.C. Epidemiology users*

#### Starting an Investigation
1. **From Patient Card**: Click "Avvia Indagine" (Start Investigation)
2. **Investigation Form**: Complete the following sections:

##### Case Classification
- **Tipo di Caso** (Case Type): Select Probable/Confirmed
- **Sintomatologia** (Symptomatology): Describe symptoms
- **Possibile Fonte di Contagio** (Possible Contagion Source): Enter details

##### Travel History
- **Permanenza in Paesi Esteri** (Foreign Travel): Yes/No
- **Paesi Visitati** (Countries Visited): List countries
- **Date di Viaggio** (Travel Dates): Enter dates

##### Diagnostic Information
- **Ricerche Diagnostiche** (Diagnostic Tests): Add test details
  - Test Type
  - Date performed
  - Testing facility
  - Results

##### Contact Information
- **Contatti del Paziente** (Patient Contacts): Add contact details
  - Relationship type (Family, Work, Social)
  - Personal data (Name, surname, tax code)
  - Profession and contact information

3. **Save Investigation**: Click "Salva Indagine" (Save Investigation)

### Disease-Specific Investigation Forms

#### CU11: Influenza Investigation
Additional fields for influenza cases:
- **Ricovero** (Hospitalization): Yes/No
- **Terapia Antivirale** (Antiviral Therapy): Yes/No
- **Malattie Croniche** (Chronic Diseases): List conditions
- **Dati di Laboratorio** (Laboratory Data): Test results for A(H1N1)v, A(H1N1), A(H3N2), B
- **Complicanze** (Complications): Describe complications
- **Esito** (Outcome): Recovery/Death

#### CU12: Botulism Investigation
Specific fields for botulism:
- **Alimento Sospetto** (Suspected Food): Food source
- **Sintomi Specifici** (Specific Symptoms): Diplopia, dysphagia
- **Diagnosi Strumentale** (Instrumental Diagnosis): Test results
- **Decorso** (Course): Hospitalization, anti-botulinum serum
- **Indagini di Laboratorio** (Laboratory Tests): Toxin searches in serum, feces, food

#### CU13-CU17: Other Disease Forms
Similar specialized forms are available for:
- **CU13**: Tetanus
- **CU14**: Encephalitis, Meningitis, Meningococcal Syndrome
- **CU15**: Legionnaires' disease
- **CU16**: Listeriosis
- **CU17**: Measles and Rubella

## Dashboard and Analytics

### CU18: Summary and Monitoring Dashboard
*Available to U.O.C. Epidemiology users*

#### Accessing the Dashboard
1. **Navigate**: Click "Dashboard" in main menu
2. **Overview Cards**: View summary statistics:
   - Total reports
   - Total investigations
   - Active patients
   - Recovered patients

#### Interactive Features
- **Time Filters**: Select daily, weekly, monthly, or yearly views
- **Region Filters**: Filter by Molise, Campania, Calabria
- **Date Range**: Select custom date ranges
- **Update**: Click "Aggiorna" (Update) to refresh data

#### Charts and Visualizations
- **Quantitative Graphs**: Reports and investigations over time
- **Pie Charts**: Disease distribution and U.O.S.D. distribution
- **Bar Charts**: Regional case distribution

### CU19: Geo-View Dashboard
*Available to U.O.C. Epidemiology users*

#### Interactive Map Features
1. **Navigate**: Click "Vista Geografica" (Geo View)
2. **Map Controls**:
   - Zoom in/out
   - Pan to different regions
   - Switch between map layers

#### Visualization Options
- **Disease Distribution**: View cases by geographic location
- **Heatmap**: See infection density in different areas
- **Cluster Analysis**: Identify outbreak clusters

#### Filtering
- **Disease Filter**: Select specific diseases to display
- **Time Period**: Filter by date range
- **Geographic Zoom**: Focus on specific regions, provinces, or municipalities

### CU20: Environmental Data Correlation Dashboard
*Available to U.O.C. Epidemiology users*

#### Correlation Analysis
1. **Navigate**: Click "Correlazioni Ambientali" (Environmental Correlations)
2. **Select Parameters**:
   - Disease type
   - Environmental factor (PM2.5, PM10, Ozone, Humidity, Temperature)
   - Geographic area
   - Time period

#### Visualization Features
- **Time-Series Graphs**: Overlay disease cases with pollutant levels
- **Correlation Coefficients**: Statistical correlation values
- **Hypothesis Testing**: Explore epidemiological relationships

## Environmental Data

### Data Import
*Available to U.O.C. Epidemiology and Admin users*

#### Excel/CSV Upload
1. **Navigate**: Go to "Dati Ambientali" (Environmental Data)
2. **Upload File**: Click "Carica File" (Upload File)
3. **Select File**: Choose Excel (.xlsx, .xls) or CSV file
4. **Format Requirements**: Ensure file includes columns:
   - istat_code
   - municipality, province, region
   - measurement_date
   - Environmental measurements (pm10, pm25, ozone, etc.)
5. **Upload**: Click "Carica" (Upload)
6. **Processing**: Monitor upload progress and error reports

#### Data Validation
- System validates data formats
- Reports errors and successful imports
- Provides batch processing status

### Data Visualization
- **Time Series**: View environmental data over time
- **Geographic Distribution**: See measurements by location
- **Correlation Analysis**: Compare with health data

## Troubleshooting

### Common Issues

#### Login Problems
**Issue**: Cannot log in
**Solutions**:
- Verify username and password are correct
- Ensure Caps Lock is not enabled
- Contact system administrator for password reset

#### Search Not Working
**Issue**: Patient search returns no results
**Solutions**:
- Check spelling of search terms
- Try partial name searches
- Search using tax code instead of name

#### Form Validation Errors
**Issue**: Cannot save forms due to validation errors
**Solutions**:
- Fill all required fields (marked with *)
- Check date formats (DD/MM/YYYY)
- Ensure numeric fields contain only numbers

#### Dashboard Not Loading
**Issue**: Dashboard shows no data
**Solutions**:
- Check date filters are not too restrictive
- Verify you have permission to view data
- Try refreshing the page
- Contact administrator if problem persists

### Getting Help

#### Contact Information
- **Technical Support**: [support email]
- **Training**: [training contact]
- **System Administrator**: [admin contact]

#### Documentation
- **User Manual**: This document
- **Video Tutorials**: [link to videos]
- **FAQ**: [link to frequently asked questions]

### System Status
If you experience widespread issues:
1. Check system status page (if available)
2. Contact other users to confirm system-wide issues
3. Report to system administrator
4. Wait for official communications about maintenance

This user manual covers all the main functions of the HealthTrace system. For additional training or support, please contact your system administrator.
