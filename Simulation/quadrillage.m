clear all
close all
% Construct a drivingScenario object.
Ts = 1; %sampling time
scenario = drivingScenario('SampleTime', Ts);

% Add all road segments
L=10;
for i=0:L
    for j=0:L
        if j<L
            roadCenters = [i*L j*L 0 ;i*L (j+1)*L 0];
            laneSpecification = lanespec(1);
            road(scenario, roadCenters, 'Lanes', laneSpecification);
        end
        if i<L
            roadCenters = [i*L j*L 0 ;(i+1)*L j*L 0];
            laneSpecification = lanespec(1);
            road(scenario, roadCenters, 'Lanes', laneSpecification);
        end
    end
end

M=L+1;

% for i=L+1:L^2-L
%     G(i,i+L)=1;
%     G(i,i-L)=1;
%     G(i-L,i)=1;
%     G(i+L,i)=1;
% end
% 
% for i=1:L
%     for j=1:L-1
%         G(j+L*(i-1),j+L*(i-1)+1)=1;
%         G(j+L*(i-1)+1,j+L*(i-1))=1;
%     end
% end
% for i=1:L-1
%     for j=1:L
%         G(j+L*(i-1),j+L*(i-1)+L)=1;
%         G(j+L*(i-1)+L,j+L*(i-1))=1;
%     end
% end

G = zeros(L^2, L^2);
for i=0:(M-1)
    for j=1:M
        if i > 0
            G((i-1)*M + j, i*M+j) = 1;
        end
        if i < M-1
            G((i+1)*M + j, i*M+j) = 1;
        end
        if j < M
            G(i*M + j+1, i*M+j) = 1;
        end
        if j > 1
            G(i*M + j-1, i*M+j) = 1;
        end
    end
end

%ajouter vehicules
Nb_car=3;      %nbre de voiture
for i=1:Nb_car
    car(i) = vehicle(scenario, 'ClassID', 1, 'Position', [0 0 0]);
    speed(i)=2;  %vitesse
    point_livraison(i,:)= [max((randi(11)-1)*L,1*L) (randi(11)-1)*L 0]  %point de livraison du coli
    T0(i)=5*i;  %date de départ de la voiture
    Livraison_OK(i)=0;      %1 = coli livré
    stop(i)=0;     %si stop=1 la voiture est à l'arret
    fin(i)=0;
end

%ajouter obstacles
Nb_Obstacles= 3*L; % nbre d'obstacles
for i=1:Nb_Obstacles
    pos_obstacle(i,:)= [max((randi(11)-1)*L,1*L) (randi(11)-1)*L 0];  %position de l'obstacle
    car(i+Nb_car) = vehicle(scenario, 'ClassID', 1, 'Position', pos_obstacle(i,:));
%     node_cancelled = pos_obstacle(i,1)*M/L + pos_obstacle(i,2)/L + 1;
%     G(node_cancelled,:)=0;
%     G(:,node_cancelled)=0;
end



plot(scenario)
hold on

for j=1:Nb_car
    scatter(point_livraison(j,1),point_livraison(j,2),20*L,"red","x",'LineWidth',3)
end



hold off

%%
point_de_passages = zeros(Nb_car,(L+1)^2);
cost = zeros(Nb_car);
for i=1:Nb_car
    [cost(i) path] = dijkstra(G,1,point_livraison(i,1)*M/L + point_livraison(i,2)/L + 1);
    a=size(path);
    point_de_passages(i,1:a(2)) = fliplr(path);
    %point_de_passages(i,a(2)+1:2*a(2)) = path;
end

avancement = zeros(Nb_car,1);
for i=1:Nb_car
    avancement(i,1)=1;
end
%%

while advance(scenario)
    for j=1:Nb_car
        
        
        
        if car(j).Position == point_livraison(j,:)
            if Livraison_OK(j) == 0
                [cost(j) path] = dijkstra(G,point_de_passages(j,avancement(j)),1);
                a=size(path);
                point_de_passages(j,:) = 0;
                point_de_passages(j,1:a(2)) = fliplr(path);
                avancement(j)=1;
                Livraison_OK(j) =1;
                'livré'
            end
        end
        
        
        if car(j).Position == [fix((point_de_passages(j,avancement(j))-1)/M)*L,rem(point_de_passages(j,avancement(j))-1,M)*L,0]
            if point_de_passages(j,avancement(j)+1) == 0
                'arrêt'
                fin(j)=1;
                scenario.StopTime=scenario.SimulationTime;
%             elseif point_de_passages(j,avancement(j)+1) == point_de_passages(j,avancement(j))
%                 Livraison_OK(j)=1;
             end
            avancement(j) = avancement(j)+1;
            end
        
            
            
        %detection des collisions
        flag_stop=zeros(1,Nb_car);
        for i=1:Nb_car+Nb_Obstacles
            if (i~=j)  
                 [zoneX,zoneY,flag_stop(i)] = distancequadrillage(car(j),car(i));
                if flag_stop(i)==1 && stop(j)==0 && fin(j)==0
                    if Livraison_OK(j) == 0
                        G(car(i).Position(1)/L * (L+1) + car(i).Position(2)/L + 1,:) = 0;
                        G(:,car(i).Position(1)/L * (L+1) + car(i).Position(2)/L +1) = 0;
                        [cost(j) path] = dijkstra(G,point_de_passages(j,max(1,avancement(j)-1)),point_livraison(j,1)*M/L + point_livraison(j,2)/L + 1);
                        a=size(path);
                        point_de_passages(j,:) = 0;
                        point_de_passages(j,1:a(2)) = fliplr(path);
                        avancement(j)=1;
                        car(j).Yaw = car(j).Yaw+180;
                    else
                        G(car(i).Position(1)/L * (L+1) + car(i).Position(2)/L + 1,:) = 0;
                        G(:,car(i).Position(1)/L * (L+1) + car(i).Position(2)/L +1) = 0;
                        [cost(j) path] = dijkstra(G,point_de_passages(j,max(1,avancement(j)-1)),1);
                        a=size(path);
                        point_de_passages(j,:) = 0;
                        point_de_passages(j,1:a(2)) = fliplr(path);
                        avancement(j)=1;
                        car(j).Yaw = car(j).Yaw+180;
                    end
                end
            end
        end
        
        if cost(j)==Inf
            'impossible'
            stop(j)=1;
            fin(j)=1;
            scenario.StopTime=scenario.SimulationTime;
        end
        
        %deplacement des voitures
        if (scenario.SimulationTime>T0(j)) && (stop(j)==0) && fin(j)==0
            [next_position, next_Yaw] = motionquadrillage(car(j),[fix((point_de_passages(j,avancement(j))-1)/M)*L,rem(point_de_passages(j,avancement(j))-1,M)*L,0],speed(j),Ts);
            car(j).Position=next_position;
            car(j).Yaw=next_Yaw;
        end
        
        
        
        
        
        
        
    end
	updatePlots(scenario) 
    pause(0.1)
end


