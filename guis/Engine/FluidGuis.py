import tkinter
import warnings
import tkinter.messagebox
import customtkinter
from PIL import Image, ImageOps
from gaslighter import convert, circle_area_from_diameter, circle_diameter_from_area
from gaslighter.fluids import IncompressibleOrifice, IntensiveState

# ALL OF THIS WAS A MISTAKE AND A HATE IT

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")


# 4E5652

def input_as_float(name: str, string: str) -> bool:
    try:
        return float(string)
    except:
       warnings.warn(f"WARNING| Could not convert {name} into a float [{string}]")

def input_converted(name: str, string: str, in_units: str, out_units: str) -> bool:
    try:
        return convert(input_as_float(name, string), in_units, out_units)
    except:
       warnings.warn(f"WARNING| Backend could not convert {name} into unit [{out_units}] form [{in_units}]")

def update_text(CTkObject, text):
    text = str(text)
    CTkObject.delete(0, 'end')
    CTkObject.insert(0, text)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.width = 1440 / 2
        self.height = 900 / 2

        # Configure window
        self.title("CustomTkinter complex_example.py")
        self.geometry(f"{self.width}x{self.height}")

        # Tabs
        self.tabview = customtkinter.CTkTabview(
            self, width=self.width, height=self.height
        )
        self.tabview.grid(row=0, column=0, padx=(0, 0), pady=(0, 0))

        # Orifice
        self.tabview.add("Orifice")
        self.tabview.tab("Orifice").grid_columnconfigure((0, 1, 2), weight=0)
        self.tabview.tab("Orifice").grid_rowconfigure((0, 1, 2), weight=0)
        self.orifice_screen()

        self.tabview.add("Pipe")
        self.tabview.tab("Pipe").grid_columnconfigure(0, weight=1)
        self.tabview.add("RocketEngine")
        self.tabview.tab("RocketEngine").grid_columnconfigure(0, weight=1)

    def user_input_dict(
        self,
        master,
        dict: dict[str, str, str],
        starting_row=1,
        label_width=60,
        input_width=100,
        units_width=60,
    ):
        # ter, text: str, input_hint: str, units_hint: str, row: int
        for i, key in enumerate(dict):
            text, input_hint, units_hint = dict[key]

            setattr(
                self,
                text,
                customtkinter.CTkLabel(master=master, text=text, width=label_width),
            )
            getattr(self, text).grid(row=starting_row + i, column=0, padx=0, pady=0)

            setattr(
                self,
                f"{text}_value",
                customtkinter.CTkEntry(
                    master, placeholder_text=input_hint, width=input_width
                ),
            )
            getattr(self, f"{text}_value").grid(
                row=starting_row + i, column=1, padx=(10,0), pady=0
            )
            getattr(self, f"{text}_value").insert(
                0, input_hint
            )

            if not units_hint == "":
                setattr(
                    self,
                    f"{text}_units",
                    customtkinter.CTkEntry(
                        master, placeholder_text=units_hint, width=units_width
                    ),
                )
                getattr(self, f"{text}_units").grid(
                    row=starting_row + i, column=2, padx=(10,0), pady=0
                )
                getattr(self, f"{text}_units").insert(0, units_hint)


    def user_dropdown_dict(
        self,
        master,
        dict: dict[str, list[str]],
        starting_row=1,
        label_width=60,
        input_width=100,
    ):
        for i, key in enumerate(dict):
            setattr(
                self,
                key,
                customtkinter.CTkLabel(master=master, text=key, width=label_width),
            )
            getattr(self, key).grid(row=starting_row + i, column=0, padx=0, pady=0)
            setattr(
                self,
                f"{key}_value",
                customtkinter.CTkOptionMenu(
                    master, values=dict[key], width=input_width
                ),
            )
            getattr(self, f"{key}_value").grid(
                row=starting_row + i, column=1, padx=(10,0), pady=0
            )


    def orifice_screen(self):

        # Main Image
        self.logo_image = customtkinter.CTkImage(
            Image.open("images/orifice.png"), size=(self.width * 0.4, self.height * 0.3)
        )
        self.logo_label = customtkinter.CTkLabel(
            self.tabview.tab("Orifice"), image=self.logo_image, text=""
        )
        self.logo_label.grid(row=0, column=0, padx=(10,0), pady=0, sticky="nsew")

        # =====================================================================
        # Geometric Props
        # =====================================================================
        self.geom_props_tab = customtkinter.CTkTabview(
            self.tabview.tab("Orifice"), width=300, height=300
        )

        self.geom_props_tab.add("Geometry")
        self.geom_props_tab.grid(row=1, column=0, padx=(10, 0 ), pady=0, sticky="nsew")
        self.user_input_dict(
            self.geom_props_tab.tab("Geometry"),
            {
                "orifice_diameter": ["Diameter", "0.5", "in"],
                "orifice_cd": ["Cd", "0.6", ""],
                "orifice_beta": ["Beta", "None", ""],
            },
        )

        self.geom_props_tab.add("Cda")
        self.user_input_dict(
            self.geom_props_tab.tab("Cda"),
            {
                "orifice_cda":["Cda", "0.127627", "in^2"],
            },
        )

        self.geom_props_tab.add("Cv")
        self.user_input_list(
            self.geom_props_tab.tab("Cv"),
            {
                "orifice_cv": ["Cv", "4.849833", ""],
            },
            label_width=60,
        )

        # =====================================================================
        # Solvers
        # =====================================================================
        self.solver_tab = customtkinter.CTkTabview(
            self.tabview.tab("Orifice"), width=300, height=300
        )
        self.solver_tab.grid(row=1, column=1, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.solver_tab.add("Solver")
        self.solver_tab.grid(
            row=1, column=1, padx=(0, 0), pady=(0, 0), sticky="nsew"
        )
        self.user_input_dict(
            self.solver_tab.tab("Solver"),
            {
                "orifice_mdot": ["Mdot", "", "lbm/s"]
            },
            starting_row=0
        )
        self.user_dropdown_dict(self.solver_tab.tab("Solver"), {
            "Method": ["Incomp", "Ideal", "Dryer"],
            "For": ["Mdot", "Geometry"]
        })
        self.solve_button = customtkinter.CTkButton(
            self.solver_tab.tab("Solver"), width=100, command=self.attempt_orifice_solution, text="Update"
        )
        self.solve_button.grid(
            row=3, column=1, padx=0, pady=0, sticky="nsew"
        )

        # =====================================================================
        # Fluid Props
        # =====================================================================
        self.fluid_props_tab = customtkinter.CTkTabview(
            self.tabview.tab("Orifice"), width=300, height=300
        )
        self.fluid_props_tab.grid(
            row=0, column=1, padx=(0, 0), pady=(0, 0), sticky="nsew"
        )
        self.fluid_props_tab.add("CoolProp")

        self.fluid = customtkinter.CTkLabel(
            self.fluid_props_tab.tab("CoolProp"), text="Fluid", width=60
        )
        self.fluid.grid(row=0, column=0, padx=(10,0), pady=0)
        self.fluid_value = customtkinter.CTkEntry(
            self.fluid_props_tab.tab("CoolProp"), placeholder_text="nitrogen", width=100
        )
        self.fluid_value.grid(row=0, column=1, padx=(10,0), pady=0)

        self.upstream = customtkinter.CTkLabel(
            self.fluid_props_tab.tab("CoolProp"), text="Upstream", width=60
        )
        self.upstream.grid(row=1, column=1, padx=(10,0), pady=0)
        self.user_input_dict(
            self.fluid_props_tab.tab("CoolProp"),
            {
                "orifice_usptream_pressure": ["Pressure", "1000.0", "psia"],
                "orifice_upstream_temp": ["Temp", "70", "degF"]
            },
            starting_row=2
        )

        self.downstream = customtkinter.CTkLabel(
            self.fluid_props_tab.tab("CoolProp"), text="Downstream", width=60
        )
        self.downstream.grid(row=4, column=1, padx=(10,0), pady=0)
        self.downstream_pressure = customtkinter.CTkLabel(
            self.fluid_props_tab.tab("CoolProp"), text="Pressure", width=60
        )
        self.downstream_pressure.grid(row=5, column=0, padx=(10,0), pady=0)
        self.downstream_pressure_value = customtkinter.CTkEntry(
            self.fluid_props_tab.tab("CoolProp"), placeholder_text="14.696", width=100
        )
        self.downstream_pressure_value.grid(row=5, column=1, padx=(10,0), pady=0)
        self.downstream_pressure_units = customtkinter.CTkEntry(
            self.fluid_props_tab.tab("CoolProp"), placeholder_text="psia", width=40
        )
        self.downstream_pressure_units.grid(row=5, column=2, padx=(10,0), pady=0)
        self.downstream_pressure_units.insert(0, "psia")

    def update_orifice_geometry(self):
        # THERE HAS TO BE A BETTER WAY
        match self.geom_props_tab.get():
            case "Geometry":
                area__m2 = circle_area_from_diameter(
                    input_converted("Diameter", self.orifice_diameter_value.get(), self.orifice_diameter_units.get(), "m")
                )
                cd = input_as_float("Cd", self.Cd_value.get())

                if self.orifice_beta.get() == ("None" or ""):
                    beta = None
                else:
                    beta = input_as_float("Beta", self.Beta_value.get())

                # Update other tabs
                update_text(self.Cda_value, str(convert(area__m2 * cd, "m^2",self.Cda_units.get())))
                update_text(self.orifice_cv_value, str(convert(area__m2 * cd, "m^2","in^2") * 38))
                update_text(self.Beta_value, str(beta))

            case "Cv":
                cda__in2 = input_as_float("Cv",self.orifice_cv_value.get()) / 38

                # Update other tabs
                update_text(self.Cda_value, str(convert(cda__in2, "in^2",self.Cda_units.get())))
                area = convert(cda__in2 / input_as_float("Cd", self.Cd_value.get()), 'in^2', f"{self.orifice_diameter_units.get()}^2")
                update_text(self.orifice_diameter_value, str(circle_diameter_from_area(area)))

            case "Cda":
                cda__in2 = input_converted("Cda", self.Cda_value.get(), self.Cda_units.get(), "in^2")
                update_text(self.orifice_cv_value, cda__in2 * 38)
                area = convert(cda__in2 / input_as_float("Cd", self.Cd_value.get()), 'in^2', f"{self.orifice_diameter_units.get()}^2")
                update_text(self.orifice_diameter_value, str(circle_diameter_from_area(area)))
            case _:
                raise ValueError("NO WAY THIS COULD EVER HAPPEN CALL ME 7477557511")


    def attempt_orifice_solution(self):
        self.update_orifice_geometry()

        # COPY AND PASTE CODE I KNOW
        area__m2 = circle_area_from_diameter(
            input_converted("Diameter", self.orifice_diameter_value.get(), self.orifice_diameter_units.get(), "m")
        )

        if self.Beta_value.get() == ("None" or ""):
            beta = None
        else:
            beta = input_as_float("Beta", self.Beta_value.get())



        # Upstream state
        upstream_state = IntensiveState(
            "P", input_converted("Upstream Pressure", self.)
        )

        match self.Method_value.get():
            case "Incomp":
                orifice = IncompressibleOrifice(
                    cd = input_as_float("Cd", self.Cd_value.get()),
                    area = area__m2,
                    fluid = self.fluid_value.get(),
                    beta_ratio=beta
                )

                if self.For_value.get() == "Mdot":
                    pass




if __name__ == "__main__":
    app = App()
    app.mainloop()
