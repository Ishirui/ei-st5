
function [next_Position next_Yaw] = motionquadrillage(car,point_livraison,v,Ts)
%determination de la prochaine position et l'orientation du vehicule
        next_Position=car.Position;
        if car.Position(1)~= point_livraison(1)
            if abs(point_livraison(1)-car.Position(1))>v*Ts
                next_Position(1)=car.Position(1)+v*Ts*sign(point_livraison(1)-car.Position(1));
            else
                next_Position(1)=point_livraison(1);
            end
            if (point_livraison(1)-car.Position(1))>0 next_Yaw = 0;else next_Yaw = 180;end
        elseif car.Position(2)~= point_livraison(2)
            if abs(point_livraison(2)-car.Position(2))>v*Ts
                next_Position(2)=car.Position(2)+v*Ts*sign(point_livraison(2)-car.Position(2));
            else
                next_Position(2)=point_livraison(2);
            end
            if (point_livraison(2)-car.Position(2))>0 next_Yaw = 90;else next_Yaw = -90;end
        else
            next_Position=car.Position;
            next_Yaw=car.Yaw;
        end
end

