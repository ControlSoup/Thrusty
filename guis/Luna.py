import tkinter
import warnings
import tkinter.messagebox
import customtkinter
from PIL import Image, ImageOps
from gaslighter import convert, circle_area_from_diameter, circle_diameter_from_area
from gaslighter.fluids import (
    DryerOrifice,
    incompressible_orifice_mdot,
    incompressible_orifice_cda,
    IntensiveState,
    ideal_orifice_mdot,
    ideal_orifice_cda,
)

# ALL OF THIS WAS A MISTAKE AND I HATE IT

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")


# 4E5652


def input_as_float(name: str, string: str) -> bool:
    try:
        return float(string)
    except Exception:
        warnings.warn(f"WARNING| Could not convert {name} into a float [{string}]")


def input_converted(name: str, string: str, in_units: str, out_units: str) -> bool:
    if not isinstance(string, str):
        raise ValueError(
            f"JOE FUCKED UP AND PASSED SOMTHING THAT IS NOT A STING TO THIS -> {type(string)}"
        )
    try:
        return convert(input_as_float(name, string), in_units, out_units)
    except Exception:
        warnings.warn(
            f"WARNING| Backend could not convert {name} into unit [{out_units}] from [{in_units}]"
        )


def update_text(CTkObject, text):
    text = str(text)
    CTkObject.delete(0, "end")
    CTkObject.insert(0, text)


def update_converted(CTkObject, value: float, in_units: str, out_units: str) -> bool:
    try:
        CTkObject.delete(0, "end")
        CTkObject.insert(0, convert(value, in_units, out_units))
    except Exception:
        warnings.warn(
            f"WARNING| Backend could not update {CTkObject.__name__} into unit [{out_units}] from [{in_units}]"
        )


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
        for i, key in enumerate(dict):
            text, input_hint, units_hint = dict[key]

            setattr(
                self,
                f"{key}_text",
                customtkinter.CTkLabel(master=master, text=text, width=label_width),
            )
            getattr(self, f"{key}_text").grid(
                row=starting_row + i, column=0, padx=0, pady=0
            )

            setattr(
                self,
                key,
                customtkinter.CTkEntry(
                    master, placeholder_text=input_hint, width=input_width
                ),
            )
            getattr(self, key).grid(
                row=starting_row + i, column=1, padx=(10, 0), pady=0
            )
            getattr(self, key).insert(0, input_hint)

            if not units_hint == "":
                setattr(
                    self,
                    f"{key}_units",
                    customtkinter.CTkEntry(
                        master, placeholder_text=units_hint, width=units_width
                    ),
                )
                getattr(self, f"{key}_units").grid(
                    row=starting_row + i, column=2, padx=(10, 0), pady=0
                )
                getattr(self, f"{key}_units").insert(0, units_hint)

    def user_dropdown_dict(
        self,
        master,
        dict: dict[str, list[str]],
        starting_row=1,
        label_width=60,
        input_width=100,
    ):
        for i, key in enumerate(dict):
            text, values = dict[key]

            setattr(
                self,
                f"{key}_text",
                customtkinter.CTkLabel(
                    master=master, text=f"{text}", width=label_width
                ),
            )
            getattr(self, f"{key}_text").grid(
                row=starting_row + i, column=0, padx=0, pady=0
            )

            setattr(
                self,
                key,
                customtkinter.CTkOptionMenu(master, width=input_width, values=values),
            )
            getattr(self, key).grid(
                row=starting_row + i, column=1, padx=(10, 0), pady=0
            )

    def orifice_screen(self):

        # Main Image
        self.logo_image = customtkinter.CTkImage(
            Image.open("images/orifice.png"), size=(self.width * 0.4, self.height * 0.3)
        )
        self.logo_label = customtkinter.CTkLabel(
            self.tabview.tab("Orifice"), image=self.logo_image, text=""
        )
        self.logo_label.grid(row=0, column=0, padx=(10, 0), pady=0, sticky="nsew")

        # =====================================================================
        # Geometric Props
        # =====================================================================
        self.geom_props_tab = customtkinter.CTkTabview(
            self.tabview.tab("Orifice"), width=300, height=300
        )

        self.geom_props_tab.add("Geometry")
        self.geom_props_tab.grid(row=1, column=0, padx=(10, 0), pady=0, sticky="nsew")
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
                "orifice_cda": ["Cda", "0.127627", "in^2"],
            },
        )

        self.geom_props_tab.add("Cv")
        self.user_input_dict(
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
        self.solver_tab.grid(row=1, column=1, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.user_input_dict(
            self.solver_tab.tab("Solver"),
            {"orifice_mdot": ["Mdot", "", "lbm/s"]},
            starting_row=0,
        )
        self.user_dropdown_dict(
            self.solver_tab.tab("Solver"),
            {
                "orifice_method": ("Method", ["Incomp", "Ideal", "Dryer"]),
                "orifice_solve_for": ("Solve For", ["Mdot", "Geometry"]),
            },
        )
        self.solve_button = customtkinter.CTkButton(
            self.solver_tab.tab("Solver"),
            width=100,
            command=self.attempt_orifice_solution,
            text="Update",
        )
        self.solve_button.grid(row=3, column=1, padx=0, pady=0, sticky="nsew")

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

        self.user_input_dict(
            self.fluid_props_tab.tab("CoolProp"),
            {"orifice_fluid": ["Fluid", "water", ""]},
            starting_row=0,
        )
        self.upstream = customtkinter.CTkLabel(
            self.fluid_props_tab.tab("CoolProp"), text="Upstream", width=60
        )
        self.upstream.grid(row=1, column=1, padx=(10, 0), pady=0)
        self.user_input_dict(
            self.fluid_props_tab.tab("CoolProp"),
            {
                "orifice_upstream_pressure": ["Pressure", "1000.0", "psia"],
                "orifice_upstream_temp": ["Temp", "70", "degF"],
            },
            starting_row=2,
        )

        self.downstream = customtkinter.CTkLabel(
            self.fluid_props_tab.tab("CoolProp"), text="Downstream", width=60
        )
        self.downstream.grid(row=4, column=1, padx=0, pady=0, sticky="nsew")
        self.user_input_dict(
            self.fluid_props_tab.tab("CoolProp"),
            {"orifice_downstream_pressure": ["Pressure", "14.696", "psia"]},
            starting_row=5,
        )

    def update_orifice_geometry(self):
        # THERE HAS TO BE A BETTER WAY
        match self.geom_props_tab.get():
            case "Geometry":
                area__m2 = circle_area_from_diameter(
                    input_converted(
                        "Diameter",
                        self.orifice_diameter.get(),
                        self.orifice_diameter_units.get(),
                        "m",
                    )
                )
                cd = input_as_float("Cd", self.orifice_cd.get())

                if self.orifice_beta.get() == ("None" or ""):
                    beta = None
                else:
                    beta = input_as_float("Beta", self.orifice_beta.get())

                # Update other tabs
                update_text(
                    self.orifice_cda,
                    str(convert(area__m2 * cd, "m^2", self.orifice_cda_units.get())),
                )
                update_text(
                    self.orifice_cv, str(convert(area__m2 * cd, "m^2", "in^2") * 38)
                )
                update_text(self.orifice_beta, str(beta))

            case "Cv":
                cda__in2 = input_as_float("Cv", self.orifice_cv.get()) / 38

                # Update other tabs
                update_text(
                    self.orifice_cda,
                    str(convert(cda__in2, "in^2", self.orifice_cda_units.get())),
                )
                area = convert(
                    cda__in2 / input_as_float("Cd", self.orifice_cd.get()),
                    "in^2",
                    f"{self.orifice_diameter_units.get()}^2",
                )
                update_text(self.orifice_diameter, str(circle_diameter_from_area(area)))

            case "Cda":
                cda__in2 = input_converted(
                    "Cda", self.orifice_cda.get(), self.orifice_cda_units.get(), "in^2"
                )
                update_text(self.orifice_cv, cda__in2 * 38)
                area = convert(
                    cda__in2 / input_as_float("Cd", self.orifice_cd.get()),
                    "in^2",
                    f"{self.orifice_diameter_units.get()}^2",
                )
                update_text(self.orifice_diameter, str(circle_diameter_from_area(area)))
            case _:
                raise ValueError("NO WAY THIS COULD EVER HAPPEN CALL ME 7477557511")

    def attempt_orifice_solution(self):

        # COPY AND PASTE CODE I KNOW
        area__m2 = circle_area_from_diameter(
            input_converted(
                "Diameter",
                self.orifice_diameter.get(),
                self.orifice_diameter_units.get(),
                "m",
            )
        )
        cda__m2 = area__m2 * input_as_float("Cd", self.orifice_cd.get())

        if self.orifice_beta.get() == ("None" or ""):
            beta = None
        else:
            beta = input_as_float("Beta", self.orifice_beta.get())

        # Upstream state
        upstream_state = IntensiveState(
            "P",
            input_converted(
                "Upstream Pressure",
                self.orifice_upstream_pressure.get(),
                self.orifice_upstream_pressure_units.get(),
                "Pa",
            ),
            "T",
            input_converted(
                "Upstream Temperature",
                self.orifice_upstream_temp.get(),
                self.orifice_upstream_temp_units.get(),
                "degK",
            ),
            fluid=self.orifice_fluid.get(),
        )

        # Downstream pressure
        downstream_pressure = input_converted(
            "Downstream Pressure",
            self.orifice_downstream_pressure.get(),
            self.orifice_downstream_pressure_units.get(),
            "Pa",
        )

        match self.orifice_method.get():
            case "Incomp":
                match self.orifice_solve_for.get():
                    case "Mdot":
                        update_converted(
                            self.orifice_mdot,
                            incompressible_orifice_mdot(
                                cda=cda__m2,
                                upstream_press=upstream_state.pressure,
                                upstream_density=upstream_state.density,
                                downstream_press=downstream_pressure,
                                beta_ratio=beta,
                            ),
                            "kg/s",
                            self.orifice_mdot_units.get(),
                        )
                    case "Geometry":
                        mdot = input_converted(
                            "Mdot",
                            self.orifice_mdot.get(),
                            self.orifice_mdot_units.get(),
                            "kg/s",
                        )
                        cda__m2 = incompressible_orifice_cda(
                            mdot=mdot,
                            upstream_press=upstream_state.pressure,
                            upstream_density=upstream_state.density,
                            downstream_press=downstream_pressure,
                            beta_ratio=beta,
                        )
                        cv = convert(cda__m2, "m^2", "in^2") * 38
                        diameter__m = circle_diameter_from_area(
                            cda__m2 / input_as_float("Cd", self.orifice_cd.get())
                        )

                        update_converted(
                            self.orifice_cda,
                            cda__m2,
                            "m^2",
                            self.orifice_cda_units.get(),
                        )
                        update_converted(
                            self.orifice_diameter,
                            diameter__m,
                            "m",
                            self.orifice_diameter_units.get(),
                        )
                        update_text(self.orifice_cv, str(cv))
                    case _:
                        raise ValueError("THIS SHOULD NEVER HAPPEN CALL ME 7477557511")

            case "Ideal":
                match self.orifice_solve_for.get():
                    case "Mdot":
                        update_converted(
                            self.orifice_mdot,
                            ideal_orifice_mdot(
                                cda=cda__m2,
                                upstream=upstream_state,
                                downstream_press=downstream_pressure,
                            ),
                            "kg/s",
                            self.orifice_mdot_units.get(),
                        )
                    case "Geometry":
                        mdot = input_converted(
                            "Mdot",
                            self.orifice_mdot.get(),
                            self.orifice_mdot_units.get(),
                            "kg/s",
                        )
                        cda__m2 = ideal_orifice_cda(
                            mdot=mdot,
                            upstream=upstream_state,
                            downstream_press=downstream_pressure,
                        )
                        cv = convert(cda__m2, "m^2", "in^2") * 38
                        diameter__m = circle_diameter_from_area(
                            cda__m2 / input_as_float("Cd", self.orifice_cd.get())
                        )

                        update_converted(
                            self.orifice_cda,
                            cda__m2,
                            "m^2",
                            self.orifice_cda_units.get(),
                        )
                        update_converted(
                            self.orifice_diameter,
                            diameter__m,
                            "m",
                            self.orifice_diameter_units.get(),
                        )
                        update_text(self.orifice_cv, str(cv))
                    case _:
                        raise ValueError("THIS SHOULD NEVER HAPPEN CALL ME 7477557511")
            case "Dryer":
                match self.orifice_solve_for.get():
                    case "Mdot":
                        dryer: DryerOrifice = DryerOrifice.from_cda(cda__m2, upstream_state.fluid)
                        update_converted(
                            self.orifice_mdot,
                            dryer.mdot(upstream_state.press, upstream_state.temp, downstream_pressure),
                            "kg/s",
                            self.orifice_mdot_units.get(),
                        )
                    case "Geometry":
                        mdot = input_converted(
                            "Mdot",
                            self.orifice_mdot.get(),
                            self.orifice_mdot_units.get(),
                            "kg/s",
                        )
                        cda__m2 = ideal_orifice_cda(
                            mdot=mdot,
                            upstream=upstream_state,
                            downstream_press=downstream_pressure,
                        )
                        cv = convert(cda__m2, "m^2", "in^2") * 38
                        diameter__m = circle_diameter_from_area(
                            cda__m2 / input_as_float("Cd", self.orifice_cd.get())
                        )

                        update_converted(
                            self.orifice_cda,
                            cda__m2,
                            "m^2",
                            self.orifice_cda_units.get(),
                        )
                        update_converted(
                            self.orifice_diameter,
                            diameter__m,
                            "m",
                            self.orifice_diameter_units.get(),
                        )
                        update_text(self.orifice_cv, str(cv))
                    case _:
                        raise ValueError("THIS SHOULD NEVER HAPPEN CALL ME 7477557511")
            case _:
                raise ValueError("THIS SHOULD NEVER HAPPEN JOE FUCKED UP CALL 7477557511")

        self.update_orifice_geometry()


if __name__ == "__main__":
    app = App()
    app.mainloop()
