import * as React from "react";
import { useLocation } from "react-router";
import { ShieldCheck } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarRail,
} from "./sidebar";
import { NavUser } from "./nav-user";
import { useUser } from "@/context/UserContext";

const data = {
  navMain: [
    // {
    //   title: "Dashboard",
    //   url: "/dashboard",
    //   items: [
    //     {
    //       title: "Portfolio Overview",
    //       url: "#",
    //     },
    //     {
    //       title: "RecentTransactions",
    //       url: "#",
    //     },
    //   ],
    // },
    {
      title: "Tranche Allocation",
      url: "/tranche",
      items: [
        { title: "Input Criteria", url: "/tranche-input" },
        { title: "Allocation Results", url: "/tranche-result" },
      ],
    },
    {
      title: "AI Insights",
      url: "/report",
      items: [
        { title: "AI-Generated Report", url: "/report" },
      ],
    },
    {
      title: "Community",
      url: "/marketplace",
      items: [
        { title: "Marketplace", url: "/marketplace" },
      ],
    },
    {
      title: "User Profile",
      items: [
        { title: "Investor Dashboard", url: "/dashboard" },
      ],
    },
  ],
};

export function AppSidebar({ ...props }) {
  const location = useLocation();
  const { user } = useUser();

  return (
    <Sidebar {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <ShieldCheck className="size-4" />
                </div>
                <div className="flex flex-col gap-0.5 leading-none">
                  <span className="font-semibold">ABSecure</span>
                  <span className="">v1.0.0</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarMenu>
            {data.navMain.map((item) => (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton asChild>
                  <a href={item.url} className="font-medium">
                    {item.title}
                  </a>
                </SidebarMenuButton>
                {item.items?.length ? (
                  <SidebarMenuSub>
                    {item.items.map((item) => (
                      <SidebarMenuSubItem key={item.title}>
                        <SidebarMenuSubButton
                          asChild
                          isActive={location.pathname === item.url}
                        >
                          <a href={item.url}>{item.title}</a>
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>
                    ))}
                  </SidebarMenuSub>
                ) : null}
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        {user ? (
          <NavUser />
        ) : (
          <p className="text-center text-sm">Not Logged In</p>
        )}
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
