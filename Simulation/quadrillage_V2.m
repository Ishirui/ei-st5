clear variables
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

G = zeros(M^2, M^2);
for i=0:M-1
    for j=0:M-1
        if i > 0
            G((i-1)*M + j + 1, i*M + j + 1) = 1;
        end
        if i < M-1
            G((i+1)*M + j + 1, i*M + j + 1) = 1;
        end
        if j < M-1
            G(i*M + j+2, i*M + j + 1) = 1;
        end
        if j > 0
            G(i*M + j, i*M + j + 1) = 1;
        end
    end
end

%ajouter vehicules
Nb_car=1;      %nbre de voiture
speed = zeros(Nb_car,1);
Nb_livraison =zeros(Nb_car,1);
point_livraison = zeros(3,3);
Livraison = zeros(Nb_car,1);
T0 = zeros(Nb_car,1);
for i=1:Nb_car
    Nb_livraison(i) = 5;
    car(i) = vehicle(scenario, 'ClassID', 1, 'Position', [0 0 0]);
    speed(i)=2;  %vitesse
    for j=1:Nb_livraison(i)
        point_livraison(j,:) = [max((randi(11)-1)*L,1*L) (randi(11)-1)*L 0];  %point de livraison du coli
    end
    T0(i)=5*i;  %date de départ de la voiture
    Livraison(i)=1;
end

%ajouter obstacles
Nb_Obstacles= 3*L; % nbre d'obstacles
pos_obstacle = zeros(Nb_Obstacles,3);
for i=1:Nb_Obstacles
    pos_obstacle(i,:)= [max((randi(11)-1)*L,1*L) (randi(11)-1)*L 0];  %position de l'obstacle
    car(i+Nb_car) = vehicle(scenario, 'ClassID', 1, 'Position', pos_obstacle(i,:));
end



plot(scenario)
hold on

for j=1:Nb_livraison
    scatter(point_livraison(j,1),point_livraison(j,2),20*L,"red","x",'LineWidth',3)
end



hold off

%%
point_de_passages = zeros(Nb_car,(L+1)^2);
cost = zeros(Nb_car,1);


for i=1:Nb_car
    [cost(i),path] = dijkstra(G,1,point_livraison(Livraison(i),1)*M/L + point_livraison(Livraison(i),2)/L + 1);
    a=size(path);
    point_de_passages(i,1:a(2)) = fliplr(path);
end

avancement = zeros(Nb_car,1);
for i=1:Nb_car
    avancement(i)=1;
end

retour = zeros(Nb_car,1);





%%

while advance(scenario)
    for j=1:Nb_car
        if Livraison(j) == Nb_livraison(j)
            if car(j).Position == point_livraison(Livraison(j),:) 
                if retour(j)==0
                    [cost(j),path] = dijkstra(G,point_de_passages(j,avancement(j)),1);
                    a=size(path);
                    point_de_passages(j,:) = 0;
                    point_de_passages(j,1:a(2)) = fliplr(path);
                    avancement(j)=1;
                    retour(j)=1;
                    disp('retour -- dernière livraison effectuée');
                end
            end 
        elseif Livraison(j) < Nb_livraison(j)
            if car(j).Position == point_livraison(Livraison(j),:)
                Livraison(j)=Livraison(j)+1;
                [cost(j),path] = dijkstra(G,point_de_passages(j,avancement(j)),point_livraison(Livraison(j),1)*M/L + point_livraison(Livraison(j),2)/L + 1);
                a=size(path);
                point_de_passages(j,:)=0;
                point_de_passages(j,1:a(2)) = fliplr(path);
                avancement(j)=1;
                disp('livraison effectuée');
            end
        end
 
        
        
        if car(j).Position == [fix((point_de_passages(j,avancement(j))-1)/M)*L,rem(point_de_passages(j,avancement(j))-1,M)*L,0]
            avancement(j) = avancement(j)+1;
        end
        
            
            
        %detection des collisions
        flag_stop=zeros(1,Nb_car);
        for i=1:Nb_car+Nb_Obstacles
            if (i~=j)  
                [zoneX,zoneY,flag_stop(i)] = distancequadrillage(car(j),car(i));
                if flag_stop(i)==1
                    G(car(i).Position(1)/L * (L+1) + car(i).Position(2)/L + 1,:) = 0;
                    G(:,car(i).Position(1)/L * (L+1) + car(i).Position(2)/L +1) = 0;
                    if retour(j)==0
                        [cost(j),path] = dijkstra(G,point_de_passages(j,max(1,avancement(j)-1)),point_livraison(Livraison(j),1)*M/L + point_livraison(Livraison(j),2)/L + 1);
                        if cost(j)==Inf
                            disp('Impossible de livrer le colis');
                            if Livraison(j) == Nb_livraison(j)
                                retour(j)=1;
                            else
                                Livraison(j) = Livraison(j)+1;
                            end
                        end
                    end
                    if retour(j)==1
                        [cost(j),path] = dijkstra(G,point_de_passages(j,max(1,avancement(j)-1)),1);
                    end
                    a=size(path);
                    point_de_passages(j,:) = 0;
                    point_de_passages(j,1:a(2)) = fliplr(path);
                    avancement(j)=1;
                    car(j).Yaw = car(j).Yaw+180;
                end
            end
        end
        
        
        
        %deplacement des voitures
        if (scenario.SimulationTime>T0(j))
            [next_position, next_Yaw] = motionquadrillage(car(j),[fix((point_de_passages(j,avancement(j))-1)/M)*L,rem(point_de_passages(j,avancement(j))-1,M)*L,0],speed(j),Ts);
            car(j).Position=next_position;
            car(j).Yaw=next_Yaw;
        end
    end
    

    
    
    if retour(j)==1
            if car(j).Position == [0 0 0]
                disp('de retour au bercail');
                scenario.StopTime = scenario.SimulationTime;
            end
    end
    
	updatePlots(scenario) 
    pause(0.1)
end


