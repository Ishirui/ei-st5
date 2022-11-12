function [zoneX,zoneY,flag_stop] = distancequadrillage(vehicle,vehicle_obstacle)
%zone devant le vehicule
if abs(rem(vehicle.Yaw,180))<2
    zoneX=sort(real([vehicle.Position(1) vehicle.Position(1)+exp(1j*pi*vehicle.Yaw/180)*2*vehicle.Length]));
    zoneY=sort(real([vehicle.Position(2)-vehicle.Length vehicle.Position(2)+vehicle.Length]));
else
    zoneX=sort(real([vehicle.Position(1)-vehicle.Length vehicle.Position(1)+vehicle.Length]));
    zoneY=sort(real([vehicle.Position(2) vehicle.Position(2)+exp(1j*pi*(vehicle.Yaw-90)/180)*2*vehicle.Length]));  
end  


% zoneX = sort([vehicle.Position(1)+vehicle.Length vehicle.Position(1)-vehicle.Length]);
% zoneY = sort([vehicle.Position(2)+vehicle.Length vehicle.Position(2)-vehicle.Length]);

if (vehicle_obstacle.Position(1)>zoneX(1)) && (vehicle_obstacle.Position(1)<zoneX(2)) && ...
   (vehicle_obstacle.Position(2)>zoneY(1)) && (vehicle_obstacle.Position(2)<zoneY(2))
     flag_stop =1;
else
     flag_stop =0;
end

end