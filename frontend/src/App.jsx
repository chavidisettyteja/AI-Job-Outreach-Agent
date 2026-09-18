import { useState } from "react";
import "./App.css";


function App() {

  // =========================================
  // INPUT STATE
  // =========================================

  const [inputMode, setInputMode] = useState("file");

  const [file, setFile] = useState(null);

  const [pastedText, setPastedText] = useState("");


  // =========================================
  // RESULT STATE
  // =========================================

  const [result, setResult] = useState(null);


  // =========================================
  // LOADING / SENDING STATE
  // =========================================

  const [loading, setLoading] = useState(false);

  const [sending, setSending] = useState(false);


  // =========================================
  // ERROR STATE
  // =========================================

  const [error, setError] = useState("");


  // =========================================
  // SEND RESULT STATE
  // =========================================

  const [sendResults, setSendResults] = useState([]);


  // =========================================
  // PROGRESS STATE
  // =========================================

  const [progress, setProgress] = useState(0);

  const [sendStatus, setSendStatus] = useState("");


  // =========================================
  // RESET ANALYSIS
  // =========================================

  const resetAnalysis = () => {

    setResult(null);

    setError("");

    setSendResults([]);

    setProgress(0);

    setSendStatus("");

  };


  // =========================================
  // CHANGE INPUT MODE
  // =========================================

  const handleInputModeChange = (mode) => {

    setInputMode(mode);

    resetAnalysis();

  };


  // =========================================
  // FILE SELECTION
  // =========================================

  const handleFileChange = (event) => {

    const selectedFile = event.target.files[0];

    if (!selectedFile) {
      return;
    }

    setFile(selectedFile);

    setPastedText("");

    resetAnalysis();

  };


  // =========================================
  // PASTED TEXT CHANGE
  // =========================================

  const handlePastedTextChange = (event) => {

    setPastedText(event.target.value);

    resetAnalysis();

  };


  // =========================================
  // ANALYZE FILE
  // =========================================

  const analyzeFile = async () => {

    if (!file) {

      setError("Please select a file first.");

      return;

    }


    setLoading(true);

    setError("");

    setResult(null);

    setSendResults([]);

    setProgress(0);

    setSendStatus("");


    const formData = new FormData();

    formData.append("file", file);


    try {

      const response = await fetch(
        // "http://127.0.0.1:8000/analyze",
        "https://ai-job-outreach-agent.onrender.com/",
        {
          method: "POST",
          body: formData
        }
      );


      const data = await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail || "Failed to analyze the file."
        );

      }


      setResult(data);

    }

    catch (err) {

      console.error(err);

      setError(err.message);

    }

    finally {

      setLoading(false);

    }

  };


  // =========================================
  // ANALYZE PASTED TEXT
  // =========================================

  const analyzePastedText = async () => {

    if (!pastedText.trim()) {

      setError(
        "Please paste a LinkedIn post, job description, or recruiter information."
      );

      return;

    }


    setLoading(true);

    setError("");

    setResult(null);

    setSendResults([]);

    setProgress(0);

    setSendStatus("");


    try {

      const response = await fetch(
        // "http://127.0.0.1:8000/analyze-text",
        "https://ai-job-outreach-agent.onrender.com/analyze-text",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            text: pastedText
          })

        }
      );


      const data = await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail || "Failed to analyze the pasted content."
        );

      }


      setResult(data);

    }

    catch (err) {

      console.error(err);

      setError(err.message);

    }

    finally {

      setLoading(false);

    }

  };


  // =========================================
  // SEND APPLICATIONS
  // =========================================

  const sendApplications = async () => {

    if (!result) {

      setError("Please analyze the content first.");

      return;

    }


    if (
      !result.contacts ||
      result.contacts.length === 0
    ) {

      setError(
        "No recruiter email addresses were found."
      );

      return;

    }


    if (!result.email) {

      setError(
        "No email was generated."
      );

      return;

    }


    if (!result.resume_selection) {

      setError(
        "No resume was selected."
      );

      return;

    }


    setSending(true);

    setSendResults([]);

    setError("");

    setProgress(0);

    setSendStatus(
      "Preparing emails..."
    );


    let progressInterval;


    try {

      // =====================================
      // VISUAL PROGRESS
      // =====================================

      let currentProgress = 0;


      progressInterval = setInterval(() => {

        currentProgress +=
          Math.floor(Math.random() * 5) + 1;


        if (currentProgress >= 90) {

          currentProgress = 90;

          setSendStatus(
            "Waiting for Gmail confirmation..."
          );

        }

        else if (currentProgress >= 70) {

          setSendStatus(
            "Sending applications..."
          );

        }

        else if (currentProgress >= 35) {

          setSendStatus(
            "Processing recruiter emails..."
          );

        }

        else {

          setSendStatus(
            "Preparing applications..."
          );

        }


        setProgress(currentProgress);


      }, 250);


      // =====================================
      // SEND REQUEST
      // =====================================

      const response = await fetch(
        // "http://127.0.0.1:8000/send",
        "https://ai-job-outreach-agent.onrender.com/send",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({

            contacts:
              result.contacts.map(
                contact => contact.email
              ),

            subject:
              result.email.subject,

            body:
              result.email.body,

            resume_type:
              result.resume_selection.resume

          })

        }
      );


      clearInterval(progressInterval);


      const data = await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to send applications."
        );

      }


      // =====================================
      // SEND RESULTS
      // =====================================

      setSendResults(
        data.results || []
      );


      // =====================================
      // COMPLETE
      // =====================================

      setProgress(100);

      setSendStatus(
        "All applications processed."
      );

    }

    catch (err) {

      if (progressInterval) {
        clearInterval(progressInterval);
      }

      console.error(err);

      setError(err.message);

      setSendStatus(
        "Sending failed."
      );

    }

    finally {

      setSending(false);

    }

  };


  // =========================================
  // SEND SUMMARY
  // =========================================

  const sentCount =
    sendResults.filter(
      item => item.status === "SENT"
    ).length;


  const failedCount =
    sendResults.filter(
      item => item.status === "FAILED"
    ).length;


  // =========================================
  // UI
  // =========================================

  return (

    <div className="app">


      {/* =====================================
          HEADER
      ===================================== */}

      <header className="top-header">

        <div className="header-content">

          <div>

            <div className="brand">

              <span className="brand-icon">
                AI
              </span>

              <span>
                Job Outreach Agent
              </span>

            </div>


            <p className="subtitle">

              AI-powered recruiter outreach automation

            </p>

          </div>


          <div className="system-status">

            <span className="status-dot"></span>

            System Ready

          </div>

        </div>

      </header>



      {/* =====================================
          MAIN DASHBOARD
      ===================================== */}

      <main className="dashboard">


        {/* ===================================
            INPUT SECTION
        =================================== */}

        <section className="upload-card">


          <div className="section-heading">

            <div>

              <span className="section-number">
                01
              </span>


              <div>

                <h2>
                  Add Job Information
                </h2>

                <p>
                  Upload a job file or paste a LinkedIn
                  post, recruiter message, or job description.
                </p>

              </div>

            </div>

          </div>



          {/* =================================
              INPUT MODE SWITCH
          ================================= */}

          <div className="input-mode">

            <button
              type="button"
              className={
                inputMode === "file"
                  ? "mode-button mode-active"
                  : "mode-button"
              }
              onClick={() =>
                handleInputModeChange("file")
              }
            >

              📄 Upload File

            </button>


            <button
              type="button"
              className={
                inputMode === "text"
                  ? "mode-button mode-active"
                  : "mode-button"
              }
              onClick={() =>
                handleInputModeChange("text")
              }
            >

              ✍️ Paste Text

            </button>

          </div>



          {/* =================================
              FILE MODE
          ================================= */}

          {inputMode === "file" && (

            <>

              <div className="upload-area">


                <div className="upload-icon">
                  ↑
                </div>


                <h3>

                  {file
                    ? file.name
                    : "Drop your job file here"}

                </h3>


                <p>
                  or select a file from your computer
                </p>


                <label className="file-button">

                  Choose File

                  <input
                    type="file"
                    onChange={handleFileChange}
                    accept=".txt,.pdf,.docx,.csv,.xlsx,.xls,.png,.jpg,.jpeg"
                  />

                </label>


                {file && (

                  <div className="selected-file">

                    <span>
                      Selected
                    </span>

                    <strong>
                      {file.name}
                    </strong>

                  </div>

                )}

              </div>


              <button
                className="primary-button analyze-button"
                onClick={analyzeFile}
                disabled={loading}
              >

                {loading
                  ? "Analyzing..."
                  : "Analyze Job"}

                {!loading && (
                  <span>
                    →
                  </span>
                )}

              </button>

            </>

          )}



          {/* =================================
              TEXT MODE
          ================================= */}

          {inputMode === "text" && (

            <div className="paste-section">


              <textarea
                className="job-textarea"

                value={pastedText}

                onChange={
                  handlePastedTextChange
                }

                placeholder={`Paste a LinkedIn post, job description, recruiter message, or HR contact information here...

Example:

Hiring AI Engineer 🚀

We are looking for an AI Engineer with experience in Python, FastAPI, LangChain and RAG.

Interested candidates can send their resume to:
rahul.mathur@sarvam.ai

Sarvam AI`}
              />


              <div className="text-helper">

                <span>
                  Paste the complete post or recruiter information.
                </span>

                <span>
                  {pastedText.length} characters
                </span>

              </div>


              <button
                className="primary-button analyze-button"
                onClick={analyzePastedText}
                disabled={
                  loading ||
                  !pastedText.trim()
                }
              >

                {loading
                  ? "Analyzing..."
                  : "Analyze Post"}

                {!loading && (
                  <span>
                    →
                  </span>
                )}

              </button>

            </div>

          )}



          {/* =================================
              ERROR
          ================================= */}

          {error && (

            <div className="error-message">

              ⚠ {error}

            </div>

          )}

        </section>



        {/* =====================================
            RESULTS
        ===================================== */}

        {result && (

          <div className="results-grid">


            {/* =================================
                CONTACTS
            ================================= */}

            <section className="card contacts-card">


              <div className="card-header">

                <div>

                  <span className="small-label">
                    CONTACTS
                  </span>

                  <h2>
                    Recruiter Information
                  </h2>

                </div>


                <div className="count-badge">

                  {result.contacts?.length || 0}

                </div>

              </div>



              <div className="contacts-list">

                {result.contacts &&
                  result.contacts.map(
                    (contact, index) => (

                      <div
                        className="contact-row"
                        key={index}
                      >


                        <div className="avatar">

                          {(contact.name || "R")
                            .charAt(0)
                            .toUpperCase()}

                        </div>



                        <div className="contact-info">

                          <strong>

                            {contact.name ||
                              "Hiring Team"}

                          </strong>


                          <span>

                            {contact.email}

                          </span>


                          <small>

                            {contact.company ||
                              "Company not specified"}

                          </small>

                        </div>

                      </div>

                    )
                  )}

              </div>

            </section>



            {/* =================================
                JOB INFORMATION
            ================================= */}

            {result.job && (

              <section className="card job-card">


                <div className="card-header">

                  <div>

                    <span className="small-label">
                      JOB ANALYSIS
                    </span>

                    <h2>
                      Job Information
                    </h2>

                  </div>


                  <div className="blue-block">
                    AI
                  </div>

                </div>



                <div className="job-title-box">

                  <span>
                    POSITION
                  </span>

                  <h3>
                    {result.job.title ||
                      "Position not specified"}
                  </h3>

                  <p>
                    {result.job.company ||
                      "Company not specified"}
                  </p>

                </div>



                {result.job.description && (

                  <div className="description">

                    {result.job.description}

                  </div>

                )}



                {result.job.skills &&
                  result.job.skills.length > 0 && (

                    <div className="skills-section">

                      <span className="small-label">
                        REQUIRED SKILLS
                      </span>


                      <div className="skills">

                        {result.job.skills.map(
                          (skill, index) => (

                            <span
                              className="skill"
                              key={index}
                            >

                              {skill}

                            </span>

                          )
                        )}

                      </div>

                    </div>

                  )}

              </section>

            )}



            {/* =================================
                NO JOB INFORMATION
            ================================= */}

            {!result.job &&
              result.resume_selection && (

                <section className="card job-card">


                  <div className="card-header">

                    <div>

                      <span className="small-label">
                        DEFAULT MODE
                      </span>

                      <h2>
                        General AI Engineer Outreach
                      </h2>

                    </div>


                    <div className="blue-block">
                      AI
                    </div>

                  </div>


                  <div className="job-title-box">

                    <span>
                      POSITION
                    </span>

                    <h3>
                      AI Engineer
                    </h3>

                    <p>
                      General Opportunity
                    </p>

                  </div>


                  <div className="description">

                    No specific job description was detected.
                    The AI Engineer resume and general AI Engineer
                    skills will be used for this outreach.

                  </div>


                  <div className="skills-section">

                    <span className="small-label">
                      AI ENGINEER SKILLS
                    </span>


                    <div className="skills">

                      {result.resume_selection.matched_skills &&
                        result.resume_selection.matched_skills.map(
                          (skill, index) => (

                            <span
                              className="skill"
                              key={index}
                            >

                              {skill}

                            </span>

                          )
                        )}

                    </div>

                  </div>

                </section>

              )}



            {/* =================================
                RESUME SELECTION
            ================================= */}

            {result.resume_selection && (

              <section className="card resume-card">


                <div className="card-header">

                  <div>

                    <span className="small-label">
                      PHASE 2
                    </span>

                    <h2>
                      Resume Selected
                    </h2>

                  </div>


                  <div className="check-icon">
                    ✓
                  </div>

                </div>



                <div className="resume-selection">


                  <div className="resume-file-icon">
                    PDF
                  </div>


                  <div>

                    <span className="resume-type">

                      {result.resume_selection.resume}

                    </span>


                    <p>

                      {result.resume_selection.resume ===
                        "AI_ENGINEER"
                        ? "AI Engineer resume selected for this outreach."
                        : "Automatically selected based on job requirements."}

                    </p>

                  </div>

                </div>



                <div className="match-section">

                  <span className="small-label">
                    MATCHED SKILLS
                  </span>


                  <div className="skills">

                    {result.resume_selection.matched_skills &&
                      result.resume_selection.matched_skills.map(
                        (skill, index) => (

                          <span
                            className="skill matched"
                            key={index}
                          >

                            ✓ {skill}

                          </span>

                        )
                      )}

                  </div>

                </div>



                <div className="reason-box">

                  <strong>
                    Selection reasoning
                  </strong>

                  <p>

                    {result.resume_selection.reason}

                  </p>

                </div>

              </section>

            )}



            {/* =================================
                EMAIL PREVIEW
            ================================= */}

            {result.email && (

              <section className="card email-card">


                <div className="card-header">

                  <div>

                    <span className="small-label">
                      PHASE 3
                    </span>

                    <h2>
                      Generated Email
                    </h2>

                  </div>


                  <div className="mail-icon">
                    ✉
                  </div>

                </div>



                <div className="email-preview">


                  <div className="email-subject">

                    <span>
                      Subject
                    </span>

                    <strong>
                      {result.email.subject}
                    </strong>

                  </div>



                  <div className="email-divider"></div>



                  <pre>
                    {result.email.body}
                  </pre>

                </div>



                {/* ===============================
                    SEND BUTTON
                =============================== */}

                <button
                  className="send-button"
                  onClick={sendApplications}
                  disabled={sending}
                >

                  <span>

                    {sending
                      ? "Sending Applications..."
                      : "Send Applications"}

                  </span>


                  <span className="send-arrow">

                    {sending
                      ? "..."
                      : "→"}

                  </span>

                </button>



                {/* ===============================
                    PROGRESS
                =============================== */}

                {(sending || progress > 0) && (

                  <div className="progress-section">


                    <div className="progress-top">

                      <div>

                        <span className="small-label">
                          OUTREACH PROGRESS
                        </span>

                        <strong>
                          {sendStatus}
                        </strong>

                      </div>


                      <span className="progress-number">
                        {progress}%
                      </span>

                    </div>



                    <div className="progress-track">

                      <div
                        className="progress-bar"
                        style={{
                          width: `${progress}%`
                        }}
                      ></div>

                    </div>



                    <div className="progress-labels">

                      <span>
                        0
                      </span>

                      <span>
                        25
                      </span>

                      <span>
                        50
                      </span>

                      <span>
                        75
                      </span>

                      <span>
                        100
                      </span>

                    </div>

                  </div>

                )}



                {/* ===============================
                    SEND RESULTS
                =============================== */}

                {sendResults.length > 0 && (

                  <div className="send-results">


                    <div className="results-summary">


                      <div className="summary-item success">

                        <strong>
                          {sentCount}
                        </strong>

                        <span>
                          Sent
                        </span>

                      </div>



                      <div className="summary-item failed">

                        <strong>
                          {failedCount}
                        </strong>

                        <span>
                          Failed
                        </span>

                      </div>



                      <div className="summary-item total">

                        <strong>
                          {sendResults.length}
                        </strong>

                        <span>
                          Total
                        </span>

                      </div>


                    </div>



                    <h3>
                      Sending Status
                    </h3>



                    <div className="sending-list">

                      {sendResults.map(
                        (item, index) => (

                          <div
                            className="sending-row"
                            key={index}
                          >


                            <div
                              className={
                                item.status === "SENT"
                                  ? "status-circle sent"
                                  : "status-circle failed"
                              }
                            >

                              {item.status === "SENT"
                                ? "✓"
                                : "!"}

                            </div>



                            <div>

                              <strong>
                                {item.email}
                              </strong>

                              <span>

                                {item.status === "SENT"
                                  ? "Application sent successfully"
                                  : "Failed to send application"}

                              </span>

                            </div>



                            <b
                              className={
                                item.status === "SENT"
                                  ? "sent-text"
                                  : "failed-text"
                              }
                            >

                              {item.status}

                            </b>

                          </div>

                        )
                      )}

                    </div>

                  </div>

                )}

              </section>

            )}

          </div>

        )}

      </main>



      {/* =====================================
          FOOTER
      ===================================== */}

      <footer>

        <span>
          AI Job Outreach Agent
        </span>

        <span>
          Phase 4 • Frontend
        </span>

      </footer>


    </div>

  );

}


export default App;