# CHATBOT FOR COLLEGE QUERIES

## Project Report

**Submitted in partial fulfillment of the requirements for the award of the degree of**  
`[Degree Name]`

**Submitted by**  
`[Student Name]`  
`[Roll Number / Enrollment Number]`

**Under the guidance of**  
`[Guide Name]`

**Department of**  
`[Department Name]`

**College Name**  
`[College Name]`

**Academic Year**  
`[2025-2026 / Submission Year]`

---

## Certificate

This is to certify that the project report entitled **"Chatbot for College Queries"** submitted by `[Student Name]` in partial fulfillment of the requirements for the award of the degree of `[Degree Name]` is a bona fide record of work carried out under my supervision and guidance.

The project work presented in this report has not been submitted elsewhere for the award of any other degree, diploma, or certificate.

**Guide Signature:** `[Signature Placeholder]`  
**Guide Name:** `[Guide Name]`  
**Head of Department:** `[HOD Name]`  
**Date:** `[Date]`

---

## Declaration

I hereby declare that the project report entitled **"Chatbot for College Queries"** is an original work carried out by me under the guidance of `[Guide Name]`. This report has not been submitted, either in full or in part, to any other university or institution for the award of any degree or diploma.

**Student Signature:** `[Signature Placeholder]`  
**Student Name:** `[Student Name]`  
**Date:** `[Date]`

---

## Acknowledgement

I express my sincere gratitude to `[Guide Name]`, my project guide, for valuable guidance, encouragement, and support throughout the development of this project. I also thank the Head of the Department, faculty members, and my college for providing the necessary facilities and academic environment for completing this work successfully.

I am thankful to my friends and family members for their motivation and support during the preparation of this project report.

---

## Abstract

The project **"Chatbot for College Queries"** is a web-based application developed to provide students with quick and automated answers to common college-related questions. In many educational institutions, students depend on office staff or faculty members to obtain information regarding admissions, fee structure, courses, attendance, examination schedules, and faculty details. This manual process often leads to delays, repetitive work, and communication gaps. The proposed chatbot addresses these issues by offering instant responses through a user-friendly web interface.

The system is designed using **HTML, CSS, and JavaScript** for the front end, **Python with Flask** for the back end, and **MySQL** for database connectivity. The chatbot uses predefined data and simple query-processing logic to match user questions with relevant responses stored in the database. An administrative interface can be used to update responses whenever institutional information changes.

The project demonstrates the practical application of web development and chatbot technology in the education sector. It improves accessibility to information, reduces manual workload for college staff, and ensures that students can obtain essential details at any time. This system is economical, easy to maintain, and suitable for deployment in academic institutions.

**Keywords:** Chatbot, College Queries, Flask, MySQL, Web Application, Student Support System

---

## Table of Contents

| Section | Page No. |
| --- | --- |
| Certificate | `____` |
| Declaration | `____` |
| Acknowledgement | `____` |
| Abstract | `____` |
| List of Figures | `____` |
| List of Tables | `____` |
| Chapter 1 - Introduction | `____` |
| Chapter 2 - Literature Review / Existing System | `____` |
| Chapter 3 - System Analysis and Requirements | `____` |
| Chapter 4 - System Design | `____` |
| Chapter 5 - Implementation | `____` |
| Chapter 6 - Testing | `____` |
| Chapter 7 - Conclusion | `____` |
| Bibliography | `____` |

> Note: Add actual page numbers after formatting the report in Word.

---

## List of Figures

| Figure No. | Title | Page No. |
| --- | --- | --- |
| Figure 1 | Homepage of the Chatbot System | `____` |
| Figure 2 | Chat Interface | `____` |
| Figure 3 | Data Flow Diagram (DFD) | `____` |
| Figure 4 | Entity Relationship Diagram (ER Diagram) | `____` |
| Figure 5 | Flowchart of Chatbot Working | `____` |
| Figure 6 | UML Use Case Diagram | `____` |
| Figure 7 | Database Table Structure | `____` |

---

## List of Tables

| Table No. | Title | Page No. |
| --- | --- | --- |
| Table 1 | Hardware Requirements | `____` |
| Table 2 | Software Requirements | `____` |
| Table 3 | Functional Requirements | `____` |
| Table 4 | Non-Functional Requirements | `____` |
| Table 5 | Database Design | `____` |
| Table 6 | Test Cases | `____` |

---

# Chapter 1 - Introduction

## 1.1 Introduction of the Project

The **Chatbot for College Queries** is a web-based application designed to answer students' questions automatically and efficiently. In a typical college environment, students often require information related to admissions, fees, attendance, courses, faculty details, examination schedules, and timetable updates. Usually, this information is obtained by visiting the college office or by contacting staff members, which may lead to delays, inconvenience, and repetitive workload.

The proposed chatbot system provides a digital solution to this problem. It allows students to access important information instantly through a web browser. By using a chatbot interface, the user can enter a question in simple language, and the system returns an appropriate response based on the stored data and predefined response logic. The application is available at any time and helps reduce the dependency on manual assistance.

This project combines web technologies and basic chatbot concepts to improve communication between students and the institution. It also demonstrates how educational services can be enhanced with automation.

## 1.2 Objectives of the Project

The main objectives of this project are as follows:

1. To provide instant replies to students' common queries.
2. To reduce the workload of office staff and faculty members.
3. To improve communication between students and the college administration.
4. To make information available 24 x 7 through an online platform.
5. To develop a simple, user-friendly, and low-cost query handling system.

## 1.3 Scope of the Project

The scope of this project is limited to handling common college-related questions through a web-based chatbot. The system can provide information related to:

- Admission process
- Course details
- Fee structure
- Examination schedules
- Attendance information
- Faculty details
- Timetable information

The project is suitable for educational institutions that need an initial automation layer for repetitive student queries. It can be expanded in the future to include multilingual support, voice interaction, AI-based understanding, and integration with student portals.

## 1.4 Problem Definition

Students often face delays when trying to obtain information from different college departments. Manual handling of repeated questions consumes time and effort for staff members. In many cases, students must physically visit the office or wait for a response during working hours. This creates inconvenience, especially during admission periods, examination schedules, or fee submission deadlines.

The proposed chatbot solves this problem by providing automatic and immediate responses to student queries. It improves the speed of communication and reduces the repetitive burden on administrative staff.

## 1.5 Significance of the Project

This project is significant because it addresses a real and common problem in academic institutions. By automating responses to frequently asked questions, the system improves service delivery and enhances the student experience. It also serves as an educational example of applying web development and database connectivity to solve practical communication challenges.

---

# Chapter 2 - Literature Review / Existing System

## 2.1 Literature Review

Chatbots have become an important part of digital communication systems in recent years. They are widely used in customer support, banking, e-commerce, healthcare, and education for handling repetitive queries. In educational institutions, chatbots can help students obtain information about admissions, academic schedules, and administrative processes without depending entirely on human staff.

Most basic chatbot systems operate using predefined rules, keyword matching, and response databases. Advanced chatbots may use natural language processing and machine learning, but for many institutional use cases, a rule-based chatbot is sufficient and economical. For a college query system, a web-based chatbot with a structured database can deliver fast and reliable responses to common questions.

The present project follows this practical approach by implementing a simple chatbot architecture using web technologies and database support. It focuses on usability, quick response, and ease of maintenance.

## 2.2 Existing System

In the traditional system, students depend on office staff, notice boards, faculty members, or department representatives for information. Queries are answered manually through face-to-face communication, phone calls, or printed notices. Although this method works, it is not always efficient when a large number of students ask similar questions.

## 2.3 Drawbacks of the Existing System

The existing manual system has the following drawbacks:

1. It is time-consuming for both students and staff.
2. It is available only during office or working hours.
3. It involves repetitive work for staff members.
4. It may lead to delayed or inconsistent responses.
5. It requires physical presence or direct contact in many cases.

## 2.4 Proposed System

The proposed system is an automated chatbot that provides instant responses to frequently asked college-related questions through a web interface. The user enters a query, the system processes the input, checks the database for a matching response, and displays the answer on the screen.

This system is developed using HTML, CSS, JavaScript, Python/Flask, and MySQL. It is designed to be simple, accessible, and easy to maintain. An administrator can update the database whenever institutional information changes.

## 2.5 Advantages of the Proposed System

The proposed system offers several advantages:

1. It provides fast responses to common queries.
2. It is available anytime through a web browser.
3. It reduces manual work for staff members.
4. It improves communication between students and the institution.
5. It offers a user-friendly interface for interaction.
6. It can be updated easily when new information is available.

## 2.6 Need for the System

Educational institutions manage a large number of students, and many queries are repetitive in nature. Handling each query manually reduces efficiency and consumes valuable time. A chatbot-based solution provides a structured and scalable method for improving the flow of information. Therefore, the development of this system is justified both academically and practically.

---

# Chapter 3 - System Analysis and Requirements

## 3.1 System Analysis

System analysis is the process of studying the requirements, structure, and behavior of a system before development. In this project, system analysis helps identify the information needs of students and the functional expectations from the chatbot. The analysis shows that the system must be simple to use, reliable, and capable of returning quick answers from stored data.

## 3.2 Hardware Requirements

**Table 1: Hardware Requirements**

| Component | Specification |
| --- | --- |
| Processor | Intel Core i3 or above |
| RAM | 4 GB minimum |
| Hard Disk | 100 GB |
| Internet Connectivity | Required for access in deployment environment |

## 3.3 Software Requirements

**Table 2: Software Requirements**

| Component | Specification |
| --- | --- |
| Operating System | Windows 10 / Windows 11 |
| Frontend | HTML, CSS, JavaScript |
| Backend | Python with Flask |
| Database | MySQL |
| Browser | Google Chrome / Edge / Firefox |
| Development Tools | Code editor, browser, local server setup |

## 3.4 Feasibility Study

### 3.4.1 Technical Feasibility

The project is technically feasible because it uses widely available tools and technologies. HTML, CSS, and JavaScript are standard technologies for building the user interface. Flask is a lightweight Python framework suitable for small and medium web applications, and MySQL provides reliable database storage. The required hardware and software are commonly available in academic environments.

### 3.4.2 Economic Feasibility

The project is economically feasible because it can be developed using free or open-source software. The implementation cost is low, and the maintenance effort is manageable. Since the system reduces manual work and improves operational efficiency, it offers good value for educational institutions.

### 3.4.3 Operational Feasibility

The proposed system is operationally feasible because it is simple to use for both students and administrators. Students can interact with the chatbot through a web browser without special training. The administrator can maintain the response data through a structured database approach. The system therefore fits well within the working environment of a college.

## 3.5 Requirement Analysis

Requirement analysis defines what the system must do and how it should perform. The requirements of this project are divided into functional and non-functional requirements.

### 3.5.1 Functional Requirements

**Table 3: Functional Requirements**

| Requirement ID | Description |
| --- | --- |
| FR1 | The user should be able to open the chatbot interface in a web browser. |
| FR2 | The user should be able to type a query related to college information. |
| FR3 | The chatbot should process the query and return an appropriate response. |
| FR4 | The system should fetch response data from the database. |
| FR5 | The administrator should be able to update chatbot responses when information changes. |
| FR6 | The system should display a message when no exact response is found. |

### 3.5.2 Non-Functional Requirements

**Table 4: Non-Functional Requirements**

| Requirement ID | Description |
| --- | --- |
| NFR1 | The system should provide fast processing and response time. |
| NFR2 | The system should be reliable and available when needed. |
| NFR3 | The system should maintain data security and controlled access to updates. |
| NFR4 | The user interface should be simple and user-friendly. |
| NFR5 | The system should be easy to maintain and update. |

## 3.6 Constraints

The present project uses predefined data and simple response logic. Therefore, the chatbot is best suited for frequently asked and structured queries. It may not fully understand highly complex or ambiguous natural language input. This limitation is acceptable for the intended scope of the project.

---

# Chapter 4 - System Design

## 4.1 Overview of System Design

System design defines how the chatbot application is organized and how different components interact. The overall design of the system includes a user interface, a backend server, a database, and query-processing logic. The user submits a question through the web interface, the backend processes the request, retrieves the appropriate response from the database, and sends the result back to the user.

## 4.2 Architecture of the System

The architecture of the proposed system consists of the following layers:

1. **Presentation Layer:** Developed using HTML, CSS, and JavaScript to provide a web-based chatbot interface.
2. **Application Layer:** Developed using Python and Flask to handle requests, process queries, and communicate with the database.
3. **Database Layer:** Developed using MySQL to store queries, responses, and administrative data.

This layered structure improves clarity, maintainability, and logical separation of responsibilities.

## 4.3 Data Flow Diagram (DFD)

### DFD Description

The Data Flow Diagram of the system can be represented as:

**User -> Chatbot Interface -> Flask Application -> MySQL Database -> Flask Application -> User Response**

### DFD Explanation

1. The user enters a query into the chatbot interface.
2. The query is sent to the Flask-based backend.
3. The backend processes the input and searches the MySQL database for a matching response.
4. The appropriate answer is retrieved from the database.
5. The response is sent back to the user through the chatbot interface.

### Figure Placeholder

**Figure 3: Data Flow Diagram (DFD)**  
Draw four entities/processes: **User**, **Chatbot Interface**, **Application Server**, and **Database**, with arrows showing the flow of query and response.

## 4.4 Entity Relationship (ER) Diagram

### Main Entities

The database design can include the following entities:

1. **User**
2. **Query**
3. **Response**
4. **Admin**

### ER Description

- A **User** submits one or more **Queries**.
- Each **Query** is mapped to a **Response**.
- An **Admin** can add, edit, or update **Responses**.

### Figure Placeholder

**Figure 4: ER Diagram**  
Show the entities **User**, **Query**, **Response**, and **Admin**, along with relationships between them.

## 4.5 Flowchart

### Flowchart Description

The flowchart of the chatbot working process can be described as follows:

1. Start
2. Display chatbot interface
3. Accept user query
4. Send query to backend
5. Search database for matching response
6. If match found, display answer
7. If no match found, display default message
8. End or wait for next query

### Figure Placeholder

**Figure 5: Flowchart of Chatbot Working**  
Create a simple flowchart with decision logic for "Match Found?" leading to either "Display Response" or "Show No Result Message".

## 4.6 UML Diagram

### Suggested UML Use Case Diagram

The UML use case diagram for this system may include the following actors and actions:

- **Student/User**
  - Ask query
  - View response
- **Admin**
  - Add response
  - Update response
  - Manage data

### Figure Placeholder

**Figure 6: UML Use Case Diagram**  
Draw two actors, **User** and **Admin**, connected to the relevant system functions.

## 4.7 Database Design

**Table 5: Database Design**

| Table Name | Important Fields | Purpose |
| --- | --- | --- |
| Users | user_id, name, email | Stores user information if login/history is maintained |
| Queries | query_id, user_id, query_text, query_date | Stores user questions |
| Responses | response_id, keyword, response_text, category | Stores chatbot answers |
| Admin | admin_id, username, password | Stores administrator details |

### Sample Table Descriptions

**Users Table:** Contains details of users interacting with the system, if such tracking is implemented.  
**Queries Table:** Stores the queries entered by users for record-keeping and future analysis.  
**Responses Table:** Stores the predefined response content used by the chatbot.  
**Admin Table:** Stores administrator login credentials and management-related information.

## 4.8 Input and Output Design

### Input Design

The main input to the system is a text-based query entered by the user through the chatbot interface. The input should be simple and related to college services such as fees, exams, courses, and admission details.

### Output Design

The output of the system is the response generated by the chatbot and displayed on the same web page. The response should be clear, relevant, and easy to understand.

---

# Chapter 5 - Implementation

## 5.1 Introduction to Implementation

Implementation is the stage in which the proposed design is converted into a working application. In this project, implementation involves creating the user interface, configuring backend logic, establishing database connectivity, and storing predefined responses for common college queries.

## 5.2 Technologies Used

The project uses the following technologies:

- **HTML** for structuring the web pages
- **CSS** for styling the chatbot interface
- **JavaScript** for client-side interaction
- **Python with Flask** for server-side programming
- **MySQL** for storing queries and responses

These technologies are selected because they are widely used, easy to understand, and suitable for academic-level web application development.

## 5.3 Modules of the System

The system can be divided into the following modules:

### 5.3.1 User Interface Module

This module provides the main chatbot page where the user enters a question and receives a response. It is developed using HTML, CSS, and JavaScript. The interface is designed to be simple, clear, and user-friendly.

### 5.3.2 Query Processing Module

This module receives the user's query and sends it to the backend application. It performs basic processing such as reading the input text and forwarding it for response matching.

### 5.3.3 Response Retrieval Module

This module searches the database for a matching keyword, category, or stored response. Once the relevant response is found, it is returned to the user through the chatbot interface.

### 5.3.4 Admin Module

This module allows the administrator to update, add, or modify chatbot responses when information changes. This helps keep the system accurate and useful over time.

### 5.3.5 Database Module

This module manages the storage of predefined responses, user queries, and administrative data. MySQL is used because it provides structured storage and efficient retrieval.

## 5.4 Working Procedure of the System

The working of the chatbot can be explained in the following steps:

1. The user opens the chatbot web page.
2. The user enters a college-related query.
3. The query is sent to the Flask backend.
4. The backend processes the text and checks the database for a matching response.
5. If a matching response is found, it is returned and displayed to the user.
6. If no matching response is available, the chatbot displays a default message such as "Please contact the college office for more details."
7. The user may continue asking additional questions.

## 5.5 Response Logic

The chatbot in this project is based on predefined data and simple intelligent behavior. Instead of using advanced machine learning models, the system relies on structured queries, keyword identification, and stored responses. This approach is suitable for handling repeated institutional questions in a controlled environment.

The advantages of this method are simplicity, low computational cost, ease of implementation, and predictable output. For a college information system, these features are practical and sufficient.

## 5.6 Security and Reliability Considerations

Basic security can be maintained by restricting admin access, validating input, and protecting database credentials. Reliability can be improved by maintaining updated response records, checking database connectivity, and testing the application under normal usage conditions.

## 5.7 Expected Output Screens

The following outputs may be included as screenshots in the final report:

- **Figure 1:** Homepage of the system
- **Figure 2:** Chat interface after entering a query
- **Figure 7:** Database table structure or admin data view

If screenshots are not yet available, these figure captions can remain as placeholders until the final formatting stage.

---

# Chapter 6 - Testing

## 6.1 Introduction to Testing

Testing is performed to verify whether the developed system works according to the expected requirements. It helps identify errors, validate functionality, and ensure that the chatbot responds correctly to user inputs.

The chatbot application can be tested manually by entering different types of college-related queries and checking whether the correct responses are displayed.

## 6.2 Types of Testing Applied

The following testing approaches are relevant to this project:

1. **Functional Testing:** To verify whether each function works correctly.
2. **Interface Testing:** To ensure the chatbot interface accepts input and displays output properly.
3. **Database Testing:** To check whether response data is retrieved correctly from MySQL.
4. **System Testing:** To validate the integrated working of the entire application.

## 6.3 Test Cases

**Table 6: Test Cases**

| Test Case ID | Test Scenario | Input | Expected Output | Result |
| --- | --- | --- | --- | --- |
| TC1 | Open chatbot page | Load website in browser | Chatbot homepage should open successfully | Pass |
| TC2 | Ask admission query | "What is the admission process?" | System should display admission-related response | Pass |
| TC3 | Ask fee query | "What is the fee structure?" | System should display fee-related response | Pass |
| TC4 | Ask exam query | "When are exams conducted?" | System should display exam schedule response | Pass |
| TC5 | Ask course query | "Which courses are available?" | System should display course details | Pass |
| TC6 | Ask unknown query | "Can you book hostel rooms?" | System should display a default or fallback response | Pass |
| TC7 | Admin updates response | Modify response record in database | Updated information should be reflected in chatbot output | Pass |

## 6.4 Result Analysis

The test results indicate that the system is capable of handling common college-related queries effectively. The chatbot provides quick responses for predefined questions and displays a fallback message when an exact answer is not available. The interface remains easy to use, and the database retrieval process supports consistent performance.

## 6.5 Limitations Observed During Testing

Since the chatbot is based on predefined responses, it may not always interpret complex or unexpected queries correctly. This limitation can be reduced in future versions by introducing improved natural language processing or more advanced query matching techniques.

---

# Chapter 7 - Conclusion

## 7.1 Conclusion

The project **"Chatbot for College Queries"** successfully demonstrates the design and development of a web-based chatbot system for educational institutions. The system is capable of answering frequently asked student queries related to admissions, fee structure, examinations, courses, attendance, faculty details, and timetable information.

By using HTML, CSS, JavaScript, Python/Flask, and MySQL, the project provides a simple yet effective solution for reducing manual workload and improving communication within a college environment. The chatbot is easy to access through a web browser and offers quick responses at any time. The project is technically feasible, economically affordable, and operationally useful for academic institutions.

Thus, the developed system meets its objectives and demonstrates the practical use of chatbot technology in the education sector.

## 7.2 Future Scope

The future enhancement of the project may include:

1. Integration of natural language processing for better understanding of user queries.
2. Voice-based interaction for improved accessibility.
3. Multilingual support for students from different language backgrounds.
4. Integration with student login systems and college portals.
5. Automatic update of information from institutional databases.
6. Mobile application support for wider accessibility.

These improvements can make the system more intelligent, interactive, and scalable.

---

## Bibliography

1. Sommerville, Ian. *Software Engineering*. Pearson Education.
2. Pressman, Roger S. *Software Engineering: A Practitioner's Approach*. McGraw-Hill.
3. Balagurusamy, E. *Programming in Python*. McGraw-Hill Education.
4. Flask Documentation. Available at: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/) `[Add access date]`
5. MySQL Documentation. Available at: [https://dev.mysql.com/doc/](https://dev.mysql.com/doc/) `[Add access date]`
6. MDN Web Docs for HTML, CSS, and JavaScript. Available at: [https://developer.mozilla.org/](https://developer.mozilla.org/) `[Add access date]`
7. W3Schools Web Technology Reference. Available at: [https://www.w3schools.com/](https://www.w3schools.com/) `[Add access date]`

---

## Final Formatting Notes

1. Replace all placeholders such as student name, guide name, department, and college name.
2. Insert actual page numbers after formatting the document in Word.
3. Add screenshots for the homepage, chat interface, and database tables if available.
4. Draw the DFD, ER diagram, flowchart, and UML diagram using Word shapes, draw.io, or any diagram tool before final submission.
5. Adjust heading styles, spacing, margins, and page breaks according to your college format.
