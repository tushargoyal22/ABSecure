import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader } from "lucide-react";
import axios from "axios";
import { useTranche } from "@/context/TrancheContext";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import Swal from "sweetalert2";

const API_URL = import.meta.env.VITE_API_URL;

const ReportViewer = () => {
  const { report, setReport, criteria, suboption, budget } = useTranche();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const fetchReport = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `${API_URL}/pool/generate_report?criterion=${criteria}&suboption=${suboption}&investor_budget=${budget}`,
        { timeout: 60000 }
      );
      const parsedReport = parseReport(response.data.report);
      setReport(parsedReport);
    } catch (error) {
      console.error("Error fetching report:", error);
      if (error.code === "ECONNABORTED") {
        Swal.fire({
          toast: true,
          position: "bottom-end",
          icon: "warning",
          title: "Request Timed Out",
          text: "The report generation is taking too long. Please try again later.",
          showConfirmButton: false,
          timer: 5000,
          timerProgressBar: true,
        });
        setErrorMessage("The request timed out. Please try again later.");
      } else {
        Swal.fire({
          toast: true,
          position: "bottom-end",
          icon: "error",
          title: "Error",
          text: "An unexpected error occurred while fetching the report.",
          showConfirmButton: false,
          timer: 5000,
          timerProgressBar: true,
        });
        setErrorMessage("Something went wrong while generating the report.");
      }
      setReport(null);
    }
    setLoading(false);
  };

  const parseReport = (reportText) => {
    const sections = reportText.split("\n\n").filter(Boolean);

    const cleanText = (text) => text.replace(/\*\*.*?\*\*/g, "").trim();

    const getSectionText = (startIndex, nextSectionIndex) => {
      return sections.slice(startIndex, nextSectionIndex).join("\n\n").trim();
    };

    const idx = sections.findIndex(
      (s) =>
        s.startsWith("\n**II. Macroeconomic Impact Analysis**") ||
        s.startsWith("**II. Macroeconomic Impact Analysis**")
    );

    return {
      securitizationType: cleanText(
        sections[
          sections.findIndex(
            (s) =>
              s.startsWith("**Securitization Type:**") ||
              s.startsWith("**I. Securitization Type:**")
          )
        ]
      ),
      underlyingAssets: cleanText(
        sections[
          sections.findIndex(
            (s) =>
              s.startsWith("**Underlying Assets:**") ||
              s.startsWith("**II. Underlying Assets:**")
          )
        ]
      ),
      investorCriteria: cleanText(
        sections[
          sections.findIndex(
            (s) =>
              s.startsWith("**Investor Selection Criteria:**") ||
              s.startsWith("**III. Investor Selection Criteria:**")
          )
        ]
      ),
      trancheAllocation:
        sections[
          sections.findIndex(
            (s, i) => i < idx && s.startsWith("| Tranche Type")
          )
        ],
      macroeconomicImpact:
        sections[
          sections.findIndex(
            (s, i) => i > idx && s.startsWith("| Tranche Type")
          )
        ],
      findings: getSectionText(
        sections.findIndex(
          (s) =>
            s.startsWith("**III. Discussion of Finding") ||
            s.startsWith("\n**III. Discussion of Finding")
        ) + 1,
        sections.findIndex(
          (s) => s.startsWith("**IV.") || s.startsWith("\n**IV.")
        )
      ),
      conclusion: getSectionText(
        sections.findIndex(
          (s) => s.startsWith("**IV.") || s.startsWith("\n**IV.")
        ) + 1,
        sections.findIndex(
          (s) => s.startsWith("**V.") || s.startsWith("\n**V.")
        )
      ),
      disclaimer: getSectionText(
        sections.findIndex(
          (s) => s.startsWith("**V.") || s.startsWith("\n**V.")
        ) + 1,
        sections.findIndex(
          (s) =>
            s.startsWith("\n**Financial Terms Explained:**") ||
            s.startsWith("**Financial Terms Explained:**")
        )
      ),
      financialTerms: getSectionText(
        sections.findIndex(
          (s) =>
            s.startsWith("\n**Financial Terms Explained:**") ||
            s.startsWith("**Financial Terms Explained:**")
        ) + 1,
        sections.length
      ),
    };
  };

  const copyToClipboard = () => {
    if (report) {
      navigator.clipboard.writeText(report);
      alert("Copied to clipboard!");
    }
  };

  const downloadPDF = () => {
    const reportElement = document.getElementById("report-content");

    if (reportElement) {
      html2canvas(reportElement, { scale: 2 }).then((canvas) => {
        const imgData = canvas.toDataURL("image/png");
        const pdf = new jsPDF("p", "mm", "a4");
        const pageHeight = 297;
        const imgWidth = 190;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        let heightLeft = imgHeight;
        let position = 10;

        pdf.addImage(imgData, "PNG", 10, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
        while (heightLeft > 0) {
          position -= pageHeight;
          pdf.addPage();
          pdf.addImage(imgData, "PNG", 10, position, imgWidth, imgHeight);
          heightLeft -= pageHeight;
        }

        pdf.save("Loan_Securitization_Report.pdf");
      });
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6">
      <Card className="shadow-2xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-lg">
        <CardHeader className="bg-gray-100 dark:bg-gray-800 rounded-t-lg p-5">
          <CardTitle className="text-2xl font-bold text-gray-900 dark:text-white">
            AI-Generated Loan Securitization Report
          </CardTitle>
        </CardHeader>

        <CardContent className="p-6 text-gray-700 dark:text-gray-300">
          {loading ? (
            <div className="flex justify-center items-center py-6">
              <Loader className="animate-spin w-6 h-6 text-blue-500 dark:text-blue-400" />
              <span className="ml-2">Generating Report...</span>
            </div>
          ) : report ? (
            <div id="report-content" className="space-y-6 animate-fade-in">
              {/* Summary */}
              <Card className="border border-gray-300 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold">
                    Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p>
                    <strong>Securitization Type:</strong>{" "}
                    {report.securitizationType}
                  </p>
                  <p>
                    <strong>Underlying Assets:</strong>{" "}
                    {report.underlyingAssets}
                  </p>
                  <p>
                    <strong>Investor Selection Criteria:</strong>{" "}
                    {report.investorCriteria}
                  </p>
                </CardContent>
              </Card>

              {/* Tranche Allocation */}
              <Card className="border border-gray-300 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold">
                    Tranche Allocation Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className="overflow-x-auto">
                  <table className="w-full border-collapse border border-gray-300 dark:border-gray-700">
                    <thead>
                      <tr className="bg-gray-100 dark:bg-gray-800">
                        <th className="border p-2">Tranche Type</th>
                        <th className="border p-2">Number of Loans</th>
                        <th className="border p-2">Total Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.macroeconomicImpact
                        .split("\n")
                        .map((row) => row.trim())
                        .filter((row) => row && row.includes("|"))
                        .slice(1)
                        .filter(
                          (row) => !/^-+$/.test(row.replace(/\|/g, "").trim())
                        )
                        .map((row, index) => {
                          const cells = row
                            .split("|")
                            .map((cell) => cell.trim())
                            .filter(Boolean);

                          return (
                            <tr key={index} className="border">
                              {cells.map((cell, i) => (
                                <td key={i} className="border p-2 text-center">
                                  {cell}
                                </td>
                              ))}
                            </tr>
                          );
                        })}
                    </tbody>
                  </table>
                </CardContent>
              </Card>

              {/* Macroeconomic Impact */}
              <Card className="border border-gray-300 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold">
                    Macroeconomic Impact Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent className="overflow-x-auto">
                  <table className="w-full border-collapse border border-gray-300 dark:border-gray-700">
                    <thead>
                      <tr className="bg-gray-100 dark:bg-gray-800">
                        <th className="border p-2">Tranche Type</th>
                        <th className="border p-2">Avg Interest Rate Impact</th>
                        <th className="border p-2">Avg Inflation Impact</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.macroeconomicImpact
                        .split("\n")
                        .map((row) => row.trim())
                        .filter((row) => row && row.includes("|"))
                        .slice(1)
                        .filter(
                          (row) => !/^-+$/.test(row.replace(/\|/g, "").trim())
                        )
                        .map((row, index) => {
                          const cells = row
                            .split("|")
                            .map((cell) => cell.trim())
                            .filter(Boolean);

                          return (
                            <tr key={index} className="border">
                              {cells.map((cell, i) => (
                                <td key={i} className="border p-2 text-center">
                                  {cell}
                                </td>
                              ))}
                            </tr>
                          );
                        })}
                    </tbody>
                  </table>
                </CardContent>
              </Card>

              {/* Findings, Conclusion, Disclaimer */}
              {["findings", "conclusion", "disclaimer"].map(
                (section, index) => (
                  <Card
                    key={index}
                    className="border border-gray-300 dark:border-gray-700"
                  >
                    <CardHeader>
                      <CardTitle className="text-lg font-semibold capitalize">
                        {section.replace(/([A-Z])/g, " $1")}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>{report[section]}</CardContent>
                  </Card>
                )
              )}

              {/* Financial Terms Explained */}
              <Card className="border border-gray-300 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold">
                    Financial Terms Explained
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc list-inside space-y-2">
                    {report.financialTerms
                      .replace(/\n\* /g, "\n• ")
                      .replace(
                        /\n\s+\* /g,
                        "\n&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                      )
                      .replace(/^\* /, "")
                      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                      .split("\n• ")
                      .map((term, index) => (
                        <li
                          key={index}
                          dangerouslySetInnerHTML={{
                            __html: term.trim().replace(/\n/g, "<br/>"),
                          }}
                        />
                      ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          ) : errorMessage ? (
            <div className="p-4 mb-4 text-red-800 bg-red-100 rounded-lg">
              {errorMessage}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400">
              Click the button below to generate the report.
            </p>
          )}

          {/* Buttons */}
          <div className="flex justify-between mt-6">
            <Button onClick={fetchReport} disabled={loading}>
              {loading ? "Generating..." : "Generate Report"}
            </Button>
            {report && (
              <>
                <Button onClick={copyToClipboard}>Copy to Clipboard</Button>
                <Button onClick={downloadPDF}>Download as PDF</Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ReportViewer;
