import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";

const terms = [
  {
    term: "Securitization",
    description:
      "The process of turning a collection of loans (like mortgages or credit card debt) into investment products called securities. These securities are then divided into tranches, allowing investors to buy shares with different risk and return profiles.",
  },
  {
    term: "Loan Pool",
    description:
      "A collection of multiple loans grouped together. These loans can come from home mortgages, car loans, or other types of debt. By combining many loans, the risk is spread out — if some loans default, others may still perform well.",
  },
  {
    term: "Tranche",
    description:
      "A tranche is a portion or slice of a larger financial pool, like a bundle of loans or mortgages. These slices are categorized based on risk level, repayment priority, and potential returns. By dividing the pool into tranches, investors can choose options that match their risk tolerance and financial goals.",
  },
  {
    term: "Senior Tranche",
    description:
      "The safest slice in the pool. Investors in this tranche are first in line to receive repayments, making it a low-risk option. Because of its safety, the returns are usually smaller, similar to earning interest on a savings account.",
  },
  {
    term: "Mezzanine Tranche",
    description:
      "A medium-risk slice that offers a balance between safety and higher returns. Investors in this tranche are paid after the senior tranche, meaning they face slightly more risk but can earn better returns.",
  },
  {
    term: "Subordinated Tranche",
    description:
      "A higher-risk slice that sits below the mezzanine tranche in repayment priority. Investors in this tranche take on greater risk but may see larger returns if the underlying assets perform well. This tranche acts as a buffer, absorbing losses before senior and mezzanine investors are affected.",
  },
  {
    term: "Equity Tranche",
    description:
      "The riskiest slice of the pool. Investors in this tranche are the last to be repaid, but if the investments perform well, they can earn the highest returns. It's a high-risk, high-reward option, similar to betting on a startup’s success.",
  },
];

const Tranche = () => {
  return (
    <div className="container mx-auto p-6">
      <Card className="mb-6 shadow-xl">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">
            Financial Terms Guide
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            This guide explains key financial terms used in the ABSecure
            platform to help you better understand your investment options.
          </p>
        </CardContent>
      </Card>

      <Accordion type="single" collapsible>
        {terms.map((item, index) => (
          <AccordionItem key={index} value={`item-${index}`}>
            <AccordionTrigger className="text-lg font-medium">
              {item.term}
            </AccordionTrigger>
            <AccordionContent className="text-gray-500">
              {item.description}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
};

export default Tranche;
