classdef FluidMechanicsCalculator
    methods(Static)
        function re = calculate_reynolds_number(rho, mu, u_inf, L)
            re = rho * u_inf * L / mu;
        end

        function Cf = calculate_friction_coefficient(re)
            Cf = 0.026 / re^(1/7);
        end

        function tau_wall = calculate_wall_shear(rho, u_inf, Cf)
            tau_wall = Cf * rho * u_inf^2 / 2;
        end

        function u_fric = calculate_fric(rho, tau_wall)
            u_fric = sqrt(tau_wall / rho);
        end
    end
end

classdef BoundaryLayerCalculator
    methods(Static)
        function delta_s = calculate_first_layer_thickness(rho, mu, u_fric, y_plus)
            delta_s = y_plus * mu / (u_fric * rho);
        end

        function delta_s_array = find_first_layer_thickness(alt_m, u_inf, L, y_plus)
            atm = Atmosphere(alt_m);
            rho = atm.density;
            mu = atm.dynamic_viscosity;
            re = FluidMechanicsCalculator.calculate_reynolds_number(rho, mu, u_inf, L);
            Cf = FluidMechanicsCalculator.calculate_friction_coefficient(re);
            tau_wall = FluidMechanicsCalculator.calculate_wall_shear(rho, u_inf, Cf);
            u_fric = FluidMechanicsCalculator.calculate_fric(rho, tau_wall);
            delta_s_array = BoundaryLayerCalculator.calculate_first_layer_thickness(rho, mu, u_fric, y_plus);
        end

        function x_transition = find_transition_x(rho, mu, u_inf, re_transition)
            x_transition = re_transition * mu / (rho * u_inf);
        end

        function delta_laminar = calculate_bl_thickness_laminar(re, x_loc)
            delta_laminar = 5 * x_loc / sqrt(re);
        end

        function delta_turbulent = calculate_bl_thickness_turbulent(re, x_loc)
            delta_turbulent = 0.37 * x_loc / re^0.2;
        end

        function delta = calculate_bl_auto(rho, mu, u_inf, x_loc, re, re_transition)
            x_transition = BoundaryLayerCalculator.find_transition_x(rho, mu, u_inf, re_transition);
            if x_loc >= x_transition
                delta = BoundaryLayerCalculator.calculate_bl_thickness_turbulent(re, x_loc);
            else
                delta = BoundaryLayerCalculator.calculate_bl_thickness_laminar(re, x_loc);
            end
        end

        function [total_thickness, thickness] = calculate_total_number_of_layers(delta_s, delta, growth_factor)
            if isscalar(delta_s)
                delta_s = [delta_s];
            end

            curr_thickness = [];
            thickness = cell(1, numel(delta_s));

            for i = 1:numel(delta_s)
                curr_delta_s = delta_s(i);
                curr_thickness_temp = curr_delta_s;
                thickness_temp = [0, curr_delta_s];

                while curr_thickness_temp <= delta
                    disp(curr_thickness_temp);
                    curr_thickness_temp = curr_thickness_temp + curr_thickness_temp * growth_factor;
                    thickness_temp = [thickness_temp, curr_thickness_temp];
                end

                curr_thickness = [curr_thickness, curr_thickness_temp];
                thickness{i} = thickness_temp;
            end

            total_thickness = curr_thickness;
        end

        function [total_thickness, thickness, delta, delta_s] = find_layers(alt_m, u_inf, L, y_plus, x_loc, re_transition, growth_factor)
            atm = Atmosphere(alt_m);
            rho = atm.density;
            mu = atm.dynamic_viscosity;
            re = FluidMechanicsCalculator.calculate_reynolds_number(rho, mu, u_inf, L);
            Cf = FluidMechanicsCalculator.calculate_friction_coefficient(re);
            tau_wall = FluidMechanicsCalculator.calculate_wall_shear(rho, u_inf, Cf);
            u_fric = FluidMechanicsCalculator.calculate_fric(rho, tau_wall);
            delta_s = BoundaryLayerCalculator.calculate_first_layer_thickness(rho, mu, u_fric, y_plus);
            delta = BoundaryLayerCalculator.calculate_bl_auto(rho, mu, u_inf, x_loc, re, re_transition);
            [total_thickness, thickness] = BoundaryLayerCalculator.calculate_total_number_of_layers(delta_s, delta, growth_factor);
        end
    end
end

function main()
    alt = 1000;
    u_inf = 1000;
    L = 4.825;
    y_plus = [5, 10];

    total_thickness = [];
    thickness = cell(1, numel(y_plus));
    delta = 0;
    delta_s = 0;

    for i = 1:numel(y_plus)
        [total_thickness_temp, thickness_temp, delta_temp, delta_s_temp] = BoundaryLayerCalculator.find_layers(alt, u_inf, L, y_plus(i), L);
        total_thickness = [total_thickness, total_thickness_temp];
        thickness{i} = thickness_temp;
        delta = delta_temp;
        delta_s = delta_s_temp;
    end

    disp(total_thickness);
    disp(thickness);
    disp(delta);
    disp(delta_s);
end

main();
