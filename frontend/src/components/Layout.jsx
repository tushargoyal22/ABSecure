import { AppSidebar } from "./ui/app-sidebar";
import { SidebarProvider, SidebarTrigger } from "./ui/sidebar";

const Layout = ({ children }) => {
  return (
    <SidebarProvider>
      <div className="flex h-screen w-full">
        <AppSidebar />
        <div className="flex flex-1 flex-col">
          <SidebarTrigger className="p-4 lg:hidden" />
          <main className="flex-1 p-6 overflow-auto">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  );
};

export default Layout;
