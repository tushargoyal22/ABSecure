import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";
import { terms } from "@/constants/config";

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
