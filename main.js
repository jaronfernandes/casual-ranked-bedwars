/*
    Casual Ranked Bedwars Bot by Jaron

    Made in January 2021 for my friends Luca, Jeffrey, Toby, Arnav, Luke, Jackson, 
    Sydney, Drew, Apple, NVP, WadWadd, and Flipchuck.

    This file is Copyright (c) 2021 - 2023 by Jaron Fernandes
*/


const Discord = require('discord.js');

const client = new Discord.Client();

const prefix = '>';

/*
    Dear Programmer:
    When I wrote this code, only God and I knew how it worked. (2021)
    Now, only God knows it! So I may have modified something (2023) and broke it.

    For this code specifically, you need to change the id of "elo_id_replacement" below to the 
    id of a message THE BOT SENDS (preferably in a HEAVILY RESTRICTED RIVATE channel)
    See line 843 to modify how new users get added to the message database.
*/

const elo_id_replacement = "795693829360975913"

// EDIT YOUR MAPS HERE
const maps = ["Lectus", "Invasion", "Katsu", "Aquarium", "Boletum", "Rise", "Chained"]

var eloChannel = null;
var eloMessage = null;
var numPlayerMsg = null

/*
eloMessage = eloChannel.messages.fetch("795693829360975913").then(async messageThing => 
    {
        eloMessage = messageThing.content.toString();
        console.log(eloMessage);
    }
);
*/

/*
const eloChannel = client.channels.cache.get("795693567744933971");
const channel = client.channels.cache.get("795693567744933971")
channel.send('greepu is hot');
eloChannel.send(`greepu is hot`);
console.log(eloChannel);
const eloMessage = eloChannel.fetch('<#795693567744933971>');
*/

var totalPlayerCount = 8;
var playersQueued = 0;

var playersEntered = [];
var playersRemaining = [];

var teamRed = [];
var teamGreen = [];

var captainOne = null;
var captainTwo = null;

var rankedSequence = 0;

var turnToPick = null;
var stringRemaining = "";

var map = "";

function compareNum(a, b)
{
    return (b.value - a.value);
}

function resetValues()
{
    totalPlayerCount = 8;
    playersQueued = 0;
    playersEntered = [];
    playersRemaining = [];
    teamRed = [];                
    teamGreen = [];
    captainOne = null;
    captainTwo = null;
    rankedSequence = 0;
    turnToPick = null;
    stringRemaining = "";
    map = "";
}

function getIndexes(string, value) {
    var indexes = [], i;
    for(i = 0; i < string.length; i++)
        if (string.charAt(i) === value)
            indexes.push(i);
    return indexes;
}

/*
        //ELO SYSTEM\\
    0 W: +35 L: -5 1ST: +15 2ND: +10 3RD: +5
    100 W: +35 L: -10 1ST: +15 2ND: +10 3RD: +5
    200 W: +30 L: -10 1ST: +15 2ND: +10 3RD: +5
    300 W: +25 L: -15 1ST: +10 2ND: +5
    400 W: +25 L: -20 1ST: +10 2ND: +5 
    500 W: +20 L: -20 1ST: +10 2ND: +5
    600 W: +15 L: -20 1ST: +10 2ND: +5
    700 W: +15 L: -25 1ST: +5 
    800 W: +10 L: -25 1ST: +5
    900 W: +10 L: -30 1ST: +5
    1000+ W: +10 L: -30
*/

function eloThingAgain(eloOrginalAmount, winOrNoOriginal, topKill, eloAddWin, eloRemoveLoss, topKillerElo, secondTop, thirdTop)
{
    eloOrginalAmount = parseInt(eloOrginalAmount)
    if(winOrNoOriginal == 'w')
    {
        eloOrginalAmount += eloAddWin;
    }
    else
    {
        eloOrginalAmount -= eloRemoveLoss;
        if (eloOrginalAmount < 0)
        {
            eloOrginalAmount = 0;
        }
    }
    if(topKill == 1)
    {
        eloOrginalAmount += topKillerElo;
    }
    else if(topKill == 2)
    {
        eloOrginalAmount += secondTop;
    }
    else if(topKill == 3)
    {
        eloOrginalAmount += thirdTop;
    }
    return eloOrginalAmount;
}

function determineElo(eloAmount, winOrNo, topKillerQuestion, userBeingScoredThingy, msg)
{
    var oldElo = 0;
    oldElo = eloAmount;
    if(eloAmount < 100) //stone
    {
        eloAmount = eloThingAgain(eloAmount,winOrNo,topKillerQuestion,35,5,15,10,5)
    }
    else if(eloAmount < 200) //iron
    {
        eloAmount = eloThingAgain(eloAmount,winOrNo,topKillerQuestion,35,10,15,10,5)
    }
    else if(eloAmount < 300) //gold 
    {
        eloAmount = eloThingAgain(eloAmount,winOrNo,topKillerQuestion,30,10,15,10,5)
    }
    else if(eloAmount < 400) //diamond 
    {
        eloAmount = eloThingAgain(eloAmount,winOrNo,topKillerQuestion,25,15,10,5,0)
    }
    else if(eloAmount < 500) //emerald
    {
        eloAmount = eloThingAgain(eloAmount,winOrNo,topKillerQuestion,25,20,10,5,0)
    }
    else if(eloAmount < 600) //sapphire
    {
        eloAmount = eloThingAgain(eloAmount,winOrNo,topKillerQuestion,20,20,10,5,0)
    }
    else if(eloAmount < 700) //ruby
    {
        eloAmount = eloThingAgain(eloAmount,winOrNo,topKillerQuestion,15,20,10,5,0)
    }
    else if(eloAmount < 800) //crystal
    {
        eloAmount = eloThingAgain(eloAmount,winOrNo,topKillerQuestion,15,25,5,0,0)
    }
    else if(eloAmount < 900) //opal
    {
        eloAmount = eloThingAgain(eloAmount,winOrNo,topKillerQuestion,10,25,5,0,0)
    }
    else if(eloAmount < 1000) //amethyst
    {
        eloAmount = eloThingAgain(eloAmount,winOrNo,topKillerQuestion,10,30,5,0,0)
    }
    else //rainbow
    {
        eloAmount = eloThingAgain(eloAmount,winOrNo,topKillerQuestion,10,30,0,0,0)
    }
    //now to give roles (sorry it's really messy)
    if(eloAmount < 100) //give stone role
    {
        if(oldElo >= 100) //check if old elo was higher
        {
            var role = msg.guild.roles.cache.find(role => role.name === "Stone [0-99]");
            userBeingScoredThingy.roles.add(role) //.roles.add(role);
            var higherRole = msg.guild.roles.cache.find(role => role.name === "Iron [100-199]");
            userBeingScoredThingy.roles.remove(higherRole) //.roles.add(role);
        }
    }
    else if(eloAmount < 200) //iron
    {
        if(oldElo < 100) //check if old elo was lower
        {
            var lowerRole = msg.guild.roles.cache.find(role => role.name === "Stone [0-99]");
            userBeingScoredThingy.roles.remove(lowerRole) //.roles.add(role);
            var role = msg.guild.roles.cache.find(role => role.name === "Iron [100-199]");
            userBeingScoredThingy.roles.add(role)
        }
        else if(oldElo >= 200) //check if old elo was higher
        {
            var role = msg.guild.roles.cache.find(role => role.name === "Iron [100-199]");
            userBeingScoredThingy.roles.add(role) //.roles.add(role);
            var higherRole = msg.guild.roles.cache.find(role => role.name === "Gold [200-299]");
            userBeingScoredThingy.roles.remove(higherRole)
        }
    }
    else if(eloAmount < 300) //gold 
    {
        if(oldElo < 200) //check if old elo was lower
        {
            var lowerRole = msg.guild.roles.cache.find(role => role.name === "Iron [100-199]");
            userBeingScoredThingy.roles.remove(lowerRole) //.roles.add(role);
            var role = msg.guild.roles.cache.find(role => role.name === "Gold [200-299]");
            userBeingScoredThingy.roles.add(role)
        }
        else if(oldElo >= 300) //check if old elo was higher
        {
            var role = msg.guild.roles.cache.find(role => role.name === "Gold [200-299]");
            userBeingScoredThingy.roles.add(role) //.roles.add(role);
            var higherRole = msg.guild.roles.cache.find(role => role.name === "Diamond [300-399]");
            userBeingScoredThingy.roles.remove(higherRole)
        }
    }
    else if(eloAmount < 400) //diamond 
    {
        if(oldElo < 300) //check if old elo was lower
        {
            var lowerRole = msg.guild.roles.cache.find(role => role.name === "Gold [200-299]");
            userBeingScoredThingy.roles.remove(lowerRole) //.roles.add(role);
            var role = msg.guild.roles.cache.find(role => role.name === "Diamond [300-399]");
            userBeingScoredThingy.roles.add(role)
        }
        else if(oldElo >= 400) //check if old elo was higher
        {
            var role = msg.guild.roles.cache.find(role => role.name === "Diamond [300-399]");
            userBeingScoredThingy.roles.add(role) //.roles.add(role);
            var higherRole = msg.guild.roles.cache.find(role => role.name === "Emerald [400-499]");
            userBeingScoredThingy.roles.remove(higherRole)
        }
    }
    else if(eloAmount < 500) //emerald
    {
        if(oldElo < 400) //check if old elo was lower
        {
            var lowerRole = msg.guild.roles.cache.find(role => role.name === "Diamond [300-399]");
            userBeingScoredThingy.roles.remove(lowerRole) //.roles.add(role);
            var role = msg.guild.roles.cache.find(role => role.name === "Emerald [400-499]");
            userBeingScoredThingy.roles.add(role)
        }
        else if(oldElo >= 500) //check if old elo was higher
        {
            var role = msg.guild.roles.cache.find(role => role.name === "Emerald [400-499]");
            userBeingScoredThingy.roles.add(role) //.roles.add(role);
            var higherRole = msg.guild.roles.cache.find(role => role.name === "Sapphire [500-599]");
            userBeingScoredThingy.roles.remove(higherRole)
        }
    }
    else if(eloAmount < 600) //sapphire
    {
        if(oldElo < 500) //check if old elo was lower
        {
            var lowerRole = msg.guild.roles.cache.find(role => role.name === "Emerald [400-499]");
            userBeingScoredThingy.roles.remove(lowerRole) //.roles.add(role);
            var role = msg.guild.roles.cache.find(role => role.name === "Sapphire [500-599]");
            userBeingScoredThingy.roles.add(role)
        }
        else if(oldElo >= 600) //check if old elo was higher
        {
            var role = msg.guild.roles.cache.find(role => role.name === "Sapphire [500-599]");
            userBeingScoredThingy.roles.add(role) //.roles.add(role);
            var higherRole = msg.guild.roles.cache.find(role => role.name === "Ruby [600-699]");
            userBeingScoredThingy.roles.remove(higherRole)
        }
    }
    else if(eloAmount < 700) //ruby
    {
        if(oldElo < 600) //check if old elo was lower
        {
            var lowerRole = msg.guild.roles.cache.find(role => role.name === "Sapphire [500-599]");
            userBeingScoredThingy.roles.remove(lowerRole) //.roles.add(role);
            var role = msg.guild.roles.cache.find(role => role.name === "Ruby [600-699]");
            userBeingScoredThingy.roles.add(role)
        }
        else if(oldElo >= 700) //check if old elo was higher
        {
            var role = msg.guild.roles.cache.find(role => role.name === "Ruby [600-699]");
            userBeingScoredThingy.roles.add(role) //.roles.add(role);
            var higherRole = msg.guild.roles.cache.find(role => role.name === "Crystal [700-799]");
            userBeingScoredThingy.roles.remove(higherRole)
        }
    }
    else if(eloAmount < 800) //crystal
    {
        if(oldElo < 700) //check if old elo was lower
        {
            var lowerRole = msg.guild.roles.cache.find(role => role.name === "Ruby [600-699]");
            userBeingScoredThingy.roles.remove(lowerRole) //.roles.add(role);
            var role = msg.guild.roles.cache.find(role => role.name === "Crystal [700-799]");
            userBeingScoredThingy.roles.add(role)
        }
        else if(oldElo >= 800) //check if old elo was higher
        {
            var role = msg.guild.roles.cache.find(role => role.name === "Crystal [700-799]");
            userBeingScoredThingy.roles.add(role) //.roles.add(role);
            var higherRole = msg.guild.roles.cache.find(role => role.name === "Opal [800-899]");
            userBeingScoredThingy.roles.remove(higherRole)
        }
    }
    else if(eloAmount < 900) //opal
    {
        if(oldElo < 800) //check if old elo was lower
        {
            var lowerRole = msg.guild.roles.cache.find(role => role.name === "Crystal [700-799]");
            userBeingScoredThingy.roles.remove(lowerRole) //.roles.add(role);
            var role = msg.guild.roles.cache.find(role => role.name === "Opal [800-899]");
            userBeingScoredThingy.roles.add(role)
        }
        else if(oldElo >= 900) //check if old elo was higher
        {
            var role = msg.guild.roles.cache.find(role => role.name === "Opal [800-899]");
            userBeingScoredThingy.roles.add(role) //.roles.add(role);
            var higherRole = msg.guild.roles.cache.find(role => role.name === "Amethyst [900-999]");
            userBeingScoredThingy.roles.remove(higherRole)
        }
    }
    else if(eloAmount < 1000) //amethyst
    {
        if(oldElo < 900) //check if old elo was lower
        {
            var lowerRole = msg.guild.roles.cache.find(role => role.name === "Opal [800-899]");
            userBeingScoredThingy.roles.remove(lowerRole) //.roles.add(role);
            var role = msg.guild.roles.cache.find(role => role.name === "Amethyst [900-999]");
            userBeingScoredThingy.roles.add(role)
        }
        else if(oldElo >= 1000) //check if old elo was higher
        {
            var role = msg.guild.roles.cache.find(role => role.name === "Amethyst [900-999]");
            userBeingScoredThingy.roles.add(role) //.roles.add(role);
            var higherRole = msg.guild.roles.cache.find(role => role.name === "Rainbow [1000+]");
            userBeingScoredThingy.roles.remove(higherRole)
        }
    }
    else //rainbow
    {
        if(oldElo < 1000) //check if old elo was lower
        {
            var lowerRole = msg.guild.roles.cache.find(role => role.name === "Amethyst [900-999]");
            userBeingScoredThingy.roles.remove(lowerRole) //.roles.add(role);
            var role = msg.guild.roles.cache.find(role => role.name === "Rainbow [1000+]");
            userBeingScoredThingy.roles.add(role) //.roles.add(role);
        }
    }
    return eloAmount;
}

client.once('ready', () => {
    console.log('my bot is online cool');
});

client.on('ready', () => {
    //console.log(eloChannel.name);
    eloChannel = client.channels.cache.get("795693567744933971");
    //eloMessage = eloChannel.fetch("795693829360975913");
    client.channels.cache.get("795693567744933971").messages.fetch(elo_id_replacement).then(async msg => 
    {
        eloMessage = await msg.content;
        //console.log("this is the elo message: "+(await eloMessage));
        //for testing purposes only!
    });
    client.user.setPresence({
        status: 'online',
        activity: {
            name: 'deer with luca (>help)',
            type: 'WATCHING'
        }
    })
    //working edit message eloMessage = eloChannel.messages.fetch("795693829360975913").then(message => message.edit("hello")).catch(console.error);
});

client.on('message', message => {
    if(!message.content.startsWith(prefix) || message.author.bot) return;

    const args = message.content.slice(prefix.length).split(/ +/);
    const command = args.shift().toLowerCase();

    if(command === 'play' && rankedSequence == 0)
    {
        message.channel.send("Enter the amount of players you'd like to play with with >(2,4,6,8).");
        rankedSequence = 1;
    } //command to start a queue
    else if ((command == '2' || command == '4' || command == '6' || command == '8') && rankedSequence == 1) 
    {
        totalPlayerCount = parseInt(command);
        message.channel.send("This ranked game will be played with "+command+" players!");
        message.channel.send("Please use >join to be entered in the queue.");
        rankedSequence = 2;
    } //command to choose how many players are playing in the queue as a total.
    else if((command == 'join' || command == 'j') && (playersQueued < totalPlayerCount) && rankedSequence == 2)
    {
        console.log(message.member.displayName);
        var stringOfName = message.author.toString();
        var canContinue = playersEntered.find(element => element == stringOfName); 
        if(!canContinue)
        {
            playersEntered.push(message.author.toString());
            message.channel.send(message.author.toString() + " has joined the queue! ("+playersEntered.length+"/"+totalPlayerCount+")");
            // && (playersQueued < totalPlayerCount) && (playersEntered.find(message.member.user)) == false && rankedSequence == 2
            playersQueued += 1;
            if(playersQueued === totalPlayerCount)
            {
                message.channel.send("The queue has reached it's limit of "+totalPlayerCount+" people.");
                playersRemaining = playersEntered;
                var randomNumOne = Math.floor(Math.random() * totalPlayerCount);
                var randomNumTwo = Math.floor(Math.random() * totalPlayerCount);
                if (randomNumTwo == randomNumOne) 
                {
                    while (randomNumTwo == randomNumOne)
                    {
                        randomNumTwo = Math.floor(Math.random() * totalPlayerCount);
                    }
                }
                captainOne = playersEntered[randomNumOne];
                captainTwo = playersEntered[randomNumTwo];
                teamRed.push(captainOne);
                teamGreen.push(captainTwo);
                playersRemaining.splice(playersRemaining.indexOf(captainOne), 1);
                playersRemaining.splice(playersRemaining.indexOf(captainTwo), 1);
                map = maps[Math.floor(Math.random() * 7)];
                //playersRemaining.splice(playersRemaining.indexOf(captainOne), 1);
                //playersRemaining.splice(playersRemaining.indexOf(captainTwo), 1);
                //message.channel.send("Team Captains are:\nRed Team: "+captainOne+"\nGreen Team: "+captainTwo);
                if(totalPlayerCount == 2)
                {
                    message.channel.send({embed: {
                        color: 3457003,
                        title: "Casual Ranked "+(totalPlayerCount/2)+"v"+(totalPlayerCount/2)+" game:",
                        fields: [
                          { name: "Red Team", value: captainOne, inline: true},
                          { name: "Green Team", value: captainTwo, inline: true},
                          { name: "Map", value: map, inline: true}
                        ]
                      }
                    });
                    message.channel.send("Starting the game. Submit a screenshot of the teams and your victory in <#795453212596764673> for it to be scored.\nA new queue may be opened up with >play.");
                    resetValues();
                }
                else
                {
                    message.channel.send({embed: {
                        color: 3457003,
                        title: "Team Captains: "+(totalPlayerCount/2)+"v"+(totalPlayerCount/2)+" game:",
                        fields: [
                          { name: "Red Team", value: captainOne, inline: true},
                          { name: "Green Team", value: captainTwo, inline: true},
                        ]
                      }
                    });
                    //message.channel.send("Team Captains are:\nRed Team: "+captainOne+"\nGreen Team: "+captainTwo);
                    if (Math.floor(Math.random() * 2) == 1)
                    {
                        message.channel.send(captainOne+" gets to pick! (>pick @player)");
                        turnToPick = captainOne;
                    }
                    else
                    {
                        message.channel.send(captainTwo+" gets to pick! (>pick @player)");
                        turnToPick = captainTwo;
                    }

                    stringRemaining = "";

                    for (var i = 0; i < playersRemaining.length; i++)
                    {   
                        if(playersRemaining[i] != captainOne && playersRemaining[i] != captainTwo)
                        {
                            stringRemaining += ", "+playersRemaining[i];
                        }
                    }
                    stringRemaining = stringRemaining.substring(2);

                    message.channel.send("Remaining players: "+stringRemaining);
                    console.log("Remaining players after captain craetion: "+stringRemaining);
                    rankedSequence = 3;
                }
            }
        }
        else
        {
            message.channel.send("bruh chill you're are already in the queue.");
        }
    } //command to join a developing queue
    else if (command == 'leave' || command == 'l')
    {   
        if(playersEntered.find(element => element == message.author.toString()))
        {
            if (rankedSequence == 2)
            {
                playersQueued -= 1;
                playersEntered.splice(playersEntered.indexOf(message.author.toString()), 1);
                message.channel.send(message.author.toString()+" has left the queue! ("+playersEntered.length+"/"+totalPlayerCount+")");
                if (playersEntered.length == 0)
                {
                    message.channel.send("Everyone has left the queue, so this game has been voided.\nUse >play if you'd like to play again!");
                    resetValues();
                }
            }
            else if(rankedSequence == 3)
            {
                message.channel.send(message.author.toString()+" has left the queue, so this game has been voided.\nUse >play if you'd like to play again!");
                resetValues();
            }
        }
        else
        {
            message.channel.send("bruh you aren't even in a queue.");
        }
    } //command to leave a developing queue
    else if (command.substring(0,4) == "pick" && message.mentions.members.first() && rankedSequence == 3 && playersEntered.length >= 2 && message.author.toString() == turnToPick)
    {
        var userRawPicked = message.content.substring(6); //slice(prefix.length).split(/ +/);
        var userPicked = userRawPicked.replace("!", "");
        if(message.mentions.members.size >= 2)
        {
            message.channel.send("don't be greedy, pick one person.");
        }
        else if(message.mentions.members.size == 1)
        {
            console.log("user picked: "+userPicked);
            console.log("author of message: "+message.author.toString())
            console.log("captainOne: "+captainOne);
            console.log("captainTwo: "+captainTwo);
            console.log("is user picked on red?: "+teamRed.includes(userPicked));
            console.log("is user picked on green?: "+teamGreen.includes(userPicked));
            console.log("is played entered?: "+playersEntered.includes(userPicked));
            if (userPicked === message.author.toString())
            {
                message.channel.send("nice try bud you can't pick yourself, pick again.");
            }
            else if(userPicked === captainOne || userPicked === captainTwo) //if something bugs with this make the == into ===
            {
                message.channel.send("good stuff bro but you can't pick a captain, pick again.");
            }
            else if(teamRed.includes(userPicked) || teamGreen.includes(userPicked))
            {
                message.channel.send("hey, they're already on a team!");
            }
            else if(playersEntered.includes(userPicked))
            {
                if(turnToPick === captainOne)
                {
                    console.log(playersRemaining.length);
                    message.channel.send(message.author.toString()+" picked "+userPicked+".");
                    playersRemaining.splice(playersRemaining.indexOf(userPicked), 1);
                    teamRed.push(userPicked);
                    turnToPick = captainTwo;                
                }
                else
                {
                    console.log(playersRemaining.length);
                    message.channel.send(message.author.toString()+" picked "+userPicked+".");
                    playersRemaining.splice(playersRemaining.indexOf(userPicked), 1);
                    teamGreen.push(userPicked);
                    turnToPick = captainOne;
                }
                if(playersRemaining.length <= 1)
                {
                    if(turnToPick == captainOne)
                    {
                        teamRed.push(playersRemaining[0]);
                    }
                    else
                    {
                        teamGreen.push(playersRemaining[0]);
                    }
                    var teamRedValue = "";
                    var teamGreenValue = "";

                    teamRedValue = teamRed[0];
                    teamGreenValue = teamGreen[0];
                    for (var i = 1; i < teamRed.length; i++)
                    {
                        teamRedValue += "\n"+teamRed[i];
                    }
                    for (var i = 1; i < teamGreen.length; i++)
                    {
                        teamGreenValue += "\n"+teamGreen[i];
                    }
                    message.channel.send({embed: {
                        color: 3457003,
                        title: "Casual Ranked "+(totalPlayerCount/2)+"v"+(totalPlayerCount/2)+" game:",
                        fields: [
                        { name: "Red Team", value: teamRedValue, inline: true},
                        { name: "Green Team", value: teamGreenValue, inline: true},
                        ]
                    }
                    });
                    message.channel.send("Starting the game. Submit a screenshot of the teams and your victory in <#795453212596764673> for it to be scored.\nA new queue may be opened up with >play.");
                    resetValues();
                }
                else
                {
                    /*
                    if(turnToPick == captainTwo)
                    {
                        message.channel.send("It is now "+captainTwo+"'s turn to pick! (>pick @player)");
                    }
                    else
                    {
                        message.channel.send("It is now "+captainOne+"'s turn to pick! (>pick @player)");
                    }
                    */
                    message.channel.send("It is now "+turnToPick+"'s turn to pick! (>pick @player)");

                    stringRemaining = "";
                    for (var i = 0; i < playersRemaining.length; i++)
                    {                           
                        if(playersRemaining[i] != captainOne && playersRemaining[i] != captainTwo)
                        {
                            stringRemaining += ", "+playersRemaining[i];
                        }
                    }
                    stringRemaining = stringRemaining.substring(2);

                    teamRedValue = "";
                    teamGreenValue = "";
                    teamRedValue = teamRed[0];
                    teamGreenValue = teamGreen[0];

                    for (var i = 1; i < teamRed.length; i++)
                    {
                        teamRedValue += "\n"+teamRed[i];
                    }
                    for (var i = 1; i < teamGreen.length; i++)
                    {
                        teamGreenValue += "\n"+teamGreen[i];
                    }
                    message.channel.send({embed: {
                        color: 3457003,
                        title: "Casual Ranked "+(totalPlayerCount/2)+"v"+(totalPlayerCount/2)+" game:",
                        fields: [
                        { name: "Red Team", value: teamRedValue, inline: true},
                        { name: "Green Team", value: teamGreenValue, inline: true},
                        { name: "Map", value: map, inline: true}
                        ]
                    }
                    });
                    message.channel.send("Remaining players: "+stringRemaining);
                    console.log("Remaining players: "+stringRemaining)
                }
            }
            else
            {
                message.channel.send("bruh either they're not in the server/queue or your format is bad (>pick @)");
            }
        }
    } //command for captains to pick players while queueing
    else if((command == 'q' || command == 'queue') && (rankedSequence == 2 || rankedSequence == 3))
    {
        if(playersEntered.length >= 1)
        {
            var formatPlayersEntered = "";
            for(var i = 0; i < playersEntered.length; i++)
            {
                formatPlayersEntered += playersEntered[i]+", ";
            }
            formatPlayersEntered.substring(0, formatPlayersEntered.length-3);
            message.channel.send({embed: {
                color: 3457003,
                title: (totalPlayerCount/2)+"v"+(totalPlayerCount/2)+" queue:",
                fields: [
                { 
                    name: "Players: ", value: formatPlayersEntered, inline: true}
                ]
            }
            });
        }
        else
        {
            message.channel.send("No one is currently queued.");
        }
    } //shows a list of all the players currently in the queue
    else if(command == 'end' && message.author.id == 293550733746241538)
    {
        resetValues();
        message.channel.send("Ended/restarted the queue. Please use >play to play again!");
    } //admin end queue command
    /*
        --
        MISCELLANEOUS COMMANDS
        --
    */
    else if(command == 'maps')
    {
        var formatMaps = "";
        for(var i = 0; i < maps.length; i++)
        {
            formatMaps += maps[i]+", ";
        }
        formatMaps.substring(0, formatMaps.length-3);
        message.channel.send({embed: {
            color: 3457003,
            title: "Season 1 Maps",
            fields: 
            [
                { name: "Current maps in rotation: ", value: formatMaps, inline: true}
            ]
          }
        });
    } //list of maps currently in rotation
    else if(command == 'season')
    {
        message.channel.send({embed: {
            color: 3457003,
            title: "Season 1",
            fields: 
            [
                { name: "Banned items: ", value: "Obsidian\nPunch Bows\nPop-up Towers", inline: true}
            ]
          }
        });
    } //season's banned items
    else if(command == 'rules')
    {
        message.channel.send({embed: {
            color: 3457003,
            title: "Rules",
            fields: 
            [
                { name: "First Rusher:", value: "Gets 28-36 iron to buy blocks and bridges to mid and 2 stacks (sometimes a mix of 1, 2, and 3 stack in some cases", inline: true},
                { name: "Second Rusher:", value: "Gets a base of 12 gold to buy iron armour, and a quantity of iron to get blocks/tools/swords", inline: true},
                { name: "Third Rusher:", value: "Drops 15-25 iron to the defender. May also get iron armour, blocks/tools/swords, and other items (fireballs)", inline: true},
                { name: "Fourth Rusher:", value: "Gets 64 + 8 iron (or 4 gold and 48 iron) to buy an endstone/wood butterfly defense, and places it down. They then follow the others to mid.", inline: true},
                
            ]
          }
        });
    } //season rules
    else if(command.substring(0,5) == 'score' && message.author.id == 293550733746241538)
    {
        var eloAndStatsForUser = [];
        var pleaseCont = false
        
        client.channels.cache.get("795693567744933971").messages.fetch(elo_id_replacement).then(async msg => 
        {
            await client.channels.cache.get("795693567744933971").messages.fetch("796780481747222549").then(async msgTwoooo => 
                {
                    numPlayerMsg = parseInt(msgTwoooo.content);
                });
            eloMessage = await msg.content;
        /*
                //ELO SYSTEM\\
            0 W: +35 L: -5 1ST: +15 2ND: +10 3RD: +5
            100 W: +35 L: -10 1ST: +15 2ND: +10 3RD: +5
            200 W: +30 L: -10 1ST: +15 2ND: +10 3RD: +5
            300 W: +25 L: -15 1ST: +10 2ND: +5
            400 W: +25 L: -20 1ST: +10 2ND: +5 
            500 W: +20 L: -20 1ST: +10 2ND: +5
            600 W: +15 L: -25 1ST: +5 
            700 W: +15 L: -30 1ST: +5 
            800 W: +10 L: -30 1ST: +5
            900 W: +10 L: -35 1ST: +5
            1000+ W: +10 L: -35
        */

        //message.channel.send("yo");

        var newElo = null;
        var userRawBeingScored = message.content.substring(7, message.content.indexOf(','));
        var userBeingScored = userRawBeingScored.replace("!", "");
        var winLoss = message.content.substring(message.content.indexOf(',')+1,message.content.indexOf(',')+2);
        var topKillerPosition = message.content.substring(message.content.indexOf('-')+1,message.content.indexOf('-')+2);
        var eloOfUser = 0; //message.content.substring(message.content.indexOf(':')+1)

        let arrayIndexesOfUsernameIdOneBruh = [];
        let arrayIndexesOfUsernameIdTwoBruh = [];
        let arrayIndexesOfELOOneBruh = [];
        let arrayIndexesOfELOTwoBruh = [];

        arrayIndexesOfUsernameIdOneBruh = getIndexes(eloMessage, "[");
        arrayIndexesOfUsernameIdTwoBruh = getIndexes(eloMessage, ",");

        arrayIndexesOfELOOneBruh = getIndexes(eloMessage, ".");
        arrayIndexesOfELOTwoBruh = getIndexes(eloMessage, "/");

        for (var i = 0; i <= arrayIndexesOfELOOneBruh.length; i++)
        {
            if (eloMessage.substring(arrayIndexesOfUsernameIdOneBruh[i]+1, arrayIndexesOfUsernameIdTwoBruh[i]) == "<@"+message.mentions.members.first().user.id+">")
            {
                console.log("<@"+message.mentions.members.first().user.id+">");
                console.log(eloMessage.substring(arrayIndexesOfUsernameIdOneBruh[i]+1, arrayIndexesOfUsernameIdTwoBruh[i]));
                eloOfUser = parseInt(eloMessage.substring(arrayIndexesOfELOOneBruh[i]+1, arrayIndexesOfELOTwoBruh[i]));
                //[myid,jaron.40/0:1;1-0] or [id,username.elo/wins:losses;games-winstreak]
                console.log(eloOfUser);
            }
        }

        console.log(userBeingScored+"'s stats this game:\nWin/Loss: "+winLoss+"\nTop Killer Position: "+topKillerPosition+"\nELO: "+eloOfUser);
        newElo = determineElo(eloOfUser, winLoss, topKillerPosition, message.mentions.members.first(), message);
        //console.log(userBeingScored.toString());
        var personPinged = message.mentions.users.first();
        //userBeingScored = personPinged;
        //message.channel.send(userBeingScored);

        message.channel.send({embed: {
            color: 3457003,
            title: "Elo Change",
            fields: 
            [
                { name: (personPinged.username)+"'s new ELO: ", value: eloOfUser+" ➜ "+newElo, inline: true}
            ]
          }
        });

        // >score @jaron,w-1:600
        // >score @jaron,l-3:300
        // >score @jaron,w-n:1000

            //console.log("this is the elo message: "+(await eloMessage));  //PUT THIS IN BRACKETS CAUSE TOO MUCH PRINT STUFF


            //this point to //scoring u take out of the async bracket!
            //eloChannel = client.channels.cache.get("795693567744933971");
        //eloChannel.messages.fetch("795693829360975913").then(messageThing => console.log(messageThing.content)).catch(console.error).toString();

        eloAndStatsForUser.push(userBeingScored, personPinged.username, newElo, winLoss);

        if(eloMessage.indexOf(userBeingScored) == -1) // Where and how new users not tracked get added. Modify this to your liking.
        {
            if(winLoss === "w")
            {
                eloChannel.messages.fetch(elo_id_replacement).then(message => message.edit(eloMessage+"["+userBeingScored+","+personPinged.username+"."+newElo+"/"+"1"+':'+"0"+";"+"1"+"-"+"1"+"]")).catch(console.error);
                eloChannel.messages.fetch("796780481747222549").then(message => message.edit(numPlayerMsg+1)).catch(console.error);
            }                                                                                                                           //[myid,jaron.40/0:1;1-0] or [id,username.elo/wins:losses;games-winstreak]
            else if(winLoss === "l")
            {
                eloChannel.messages.fetch(elo_id_replacement).then(message => message.edit(eloMessage+"["+userBeingScored+","+personPinged.username+"."+newElo+"/"+"0"+':'+"1"+";"+"1"+"-"+"0"+"]")).catch(console.error);
                eloChannel.messages.fetch("796780481747222549").then(message => message.edit(numPlayerMsg+1)).catch(console.error);
            }                                                                                                                           //[myid,jaron.40/0:1;1-0] or [id,username.elo/wins:losses;games-winstreak]
        }
        else
        {
            var indexOfPerson = eloMessage.indexOf(userBeingScored);
            var winsOfPerson = parseInt(eloMessage.substring(eloMessage.indexOf("/", indexOfPerson)+1, eloMessage.indexOf(":", indexOfPerson)));
            var lossesOfPerson = parseInt(eloMessage.substring(eloMessage.indexOf(":", indexOfPerson)+1, eloMessage.indexOf(";", indexOfPerson)));
            var gamesOfPerson = parseInt(eloMessage.substring(eloMessage.indexOf(";", indexOfPerson)+1, eloMessage.indexOf("-", indexOfPerson)));
            var winstreakOfPerson = parseInt(eloMessage.substring(eloMessage.indexOf("-", indexOfPerson)+1, eloMessage.indexOf("]", indexOfPerson)));
            gamesOfPerson += 1;
            if(winLoss === "w")
            {
                winsOfPerson += 1;
                winstreakOfPerson += 1;
                var newEloMessage = eloMessage.replace(eloMessage.substring(indexOfPerson-1, eloMessage.indexOf("]", indexOfPerson)+1), "");
                eloChannel.messages.fetch(elo_id_replacement).then(message => message.edit(newEloMessage+"["+userBeingScored+","+personPinged.username+"."+newElo+"/"+winsOfPerson+':'+lossesOfPerson+";"+gamesOfPerson+"-"+winstreakOfPerson+"]")).catch(console.error);
            }
            else if(winLoss === "l")
            {
                lossesOfPerson += 1;
                winstreakOfPerson = "0";
                var newEloMessage = eloMessage.replace(eloMessage.substring(indexOfPerson-1, eloMessage.indexOf("]", indexOfPerson)+1), "");
                eloChannel.messages.fetch(elo_id_replacement).then(message => message.edit(newEloMessage+"["+userBeingScored+","+personPinged.username+"."+newElo+"/"+winsOfPerson+':'+lossesOfPerson+";"+gamesOfPerson+"-"+winstreakOfPerson+"]")).catch(console.error);
            }
        }

        //message.edit(content="the new content of the message");
        }); //gets the database message
        
    } //scoring
    else if(command == 'stats' && message.mentions.members.size <= 1)
    {
        if(message.mentions.members.size == 0)
        {
            client.channels.cache.get("795693567744933971").messages.fetch(elo_id_replacement).then(async msg => 
            {
                eloMessage = await msg.content;
                //console.log("this is the elo message: "+(await eloMessage)); //PUT THIS IN BRACKETS CAUSE TOO MUCH PRINT STUFF
                if (eloMessage.indexOf(message.author.toString()) == -1)
                {
                    var embeddedMessage = new Discord.MessageEmbed()
                    .setTitle(message.author.username+"'s stats")
                    .setColor(3457003)
                    .setImage(message.author.avatarURL())
                    .addField("ELO: ", "0", true)
                    .addField("Wins: ", "0", true)
                    .addField("Losses: ", "0", true)
                    .addField("Win/Loss Ratio: ", "0", true)
                    .addField("Games: ", "0", true)
                    .addField("Winstreak: ", "0", true)
                    message.channel.send(embeddedMessage);
                } //checks to see if people have stats in the first place
                else
                {
                    var indexOfPersonThing = eloMessage.indexOf(message.author.toString());
                    var eloOfPersonThing = parseInt(eloMessage.substring(eloMessage.indexOf(".", indexOfPersonThing)+1, eloMessage.indexOf("/", indexOfPersonThing)));
                    var winsOfPersonThing = parseInt(eloMessage.substring(eloMessage.indexOf("/", indexOfPersonThing)+1, eloMessage.indexOf(":", indexOfPersonThing)));
                    var lossesOfPersonThing = parseInt(eloMessage.substring(eloMessage.indexOf(":", indexOfPersonThing)+1, eloMessage.indexOf(";", indexOfPersonThing)));
                    var gamesOfPersonThing = parseInt(eloMessage.substring(eloMessage.indexOf(";", indexOfPersonThing)+1, eloMessage.indexOf("-", indexOfPersonThing)));
                    var winstreakOfPersonThing = parseInt(eloMessage.substring(eloMessage.indexOf("-", indexOfPersonThing)+1, eloMessage.indexOf("]", indexOfPersonThing)));
                    var wlr = (winsOfPersonThing/lossesOfPersonThing).toFixed(2);

                    var embeddedMessage = new Discord.MessageEmbed()
                    .setTitle(message.author.username+"'s stats")
                    .setColor(3457003)
                    .setImage(message.author.avatarURL())
                    .addField("ELO: ", eloOfPersonThing, true)
                    .addField("Wins: ", winsOfPersonThing, true)
                    .addField("Losses: ", lossesOfPersonThing, true)
                    .addField("Win/Loss Ratio: ", wlr, true)
                    .addField("Games: ", gamesOfPersonThing, true)
                    .addField("Winstreak: ", winstreakOfPersonThing, true)

                    message.channel.send(embeddedMessage);
                } //the rest who already do have stats in the database
            });
        }
        else
        {
            client.channels.cache.get("795693567744933971").messages.fetch(elo_id_replacement).then(async msg => 
            {
                eloMessage = await msg.content;
                //console.log("this is the elo message: "+(await eloMessage)); //PUT THIS IN BRACKETS CAUSE TOO MUCH PRINT STUFF
                if (eloMessage.indexOf("<@"+message.mentions.members.first().id+">") == -1)
                {
                    var embeddedMessage = new Discord.MessageEmbed()
                    .setTitle(message.mentions.members.first().user.username+"'s stats")
                    .setColor(3457003)
                    .setImage(message.mentions.members.first().user.avatarURL())
                    .addField("ELO: ", "0", true)
                    .addField("Wins: ", "0", true)
                    .addField("Losses: ", "0", true)
                    .addField("Win/Loss Ratio: ", "0", true)
                    .addField("Games: ", "0", true)
                    .addField("Winstreak: ", "0", true)
                    message.channel.send(embeddedMessage);
                } //checks to see if people have stats in the first place
                else
                {
                    var indexOfPersonThing = eloMessage.indexOf("<@"+message.mentions.members.first().id+">".toString());
                    var eloOfPersonThing = parseInt(eloMessage.substring(eloMessage.indexOf(".", indexOfPersonThing)+1, eloMessage.indexOf("/", indexOfPersonThing)));
                    var winsOfPersonThing = parseInt(eloMessage.substring(eloMessage.indexOf("/", indexOfPersonThing)+1, eloMessage.indexOf(":", indexOfPersonThing)));
                    var lossesOfPersonThing = parseInt(eloMessage.substring(eloMessage.indexOf(":", indexOfPersonThing)+1, eloMessage.indexOf(";", indexOfPersonThing)));
                    var gamesOfPersonThing = parseInt(eloMessage.substring(eloMessage.indexOf(";", indexOfPersonThing)+1, eloMessage.indexOf("-", indexOfPersonThing)));
                    var winstreakOfPersonThing = parseInt(eloMessage.substring(eloMessage.indexOf("-", indexOfPersonThing)+1, eloMessage.indexOf("]", indexOfPersonThing)));
                    var wlr = (winsOfPersonThing/lossesOfPersonThing).toFixed(2);
                    /*
                    if (wlr == Number.POSITIVE_INFINITY)
                    {
                        wlr = winsOfPersonThing;
                    }
                    */ //infinity check
                    var embeddedMessage = new Discord.MessageEmbed()
                    .setTitle(message.mentions.members.first().user.username+"'s stats")
                    .setColor(3457003)
                    .setImage(message.mentions.members.first().user.avatarURL())
                    .addField("ELO: ", eloOfPersonThing, true)
                    .addField("Wins: ", winsOfPersonThing, true)
                    .addField("Losses: ", lossesOfPersonThing, true)
                    .addField("Win/Loss Ratio: ", wlr, true)
                    .addField("Games: ", gamesOfPersonThing, true)
                    .addField("Winstreak: ", winstreakOfPersonThing, true)
    
                    message.channel.send(embeddedMessage);
                } //the rest who already do have stats in the database
            });
        }
    }
    else if(command == 'lb')
    {
        client.channels.cache.get("795693567744933971").messages.fetch(elo_id_replacement).then(async msg => 
        {
            var statsMsg = await msg.content;
            statsMsg.replace("%", "");
            var numThing = 0;
            await client.channels.cache.get("795693567744933971").messages.fetch("796780481747222549").then(async bruhMsg => 
            {
                numThing = await bruhMsg.content;
                numThing = parseInt(numThing);
            });
            //tableOfBruhStats.sort();
            //console.log("this is the elo message: "+(await eloMessage)); //PUT THIS IN BRACKETS CAUSE TOO MUCH PRINT STUFF
            if (message.content.includes("wins") == true)
            {
                //console.log("got inside wins");
                let tableOfBruhStats = [];
                let arrayIndexesOfUsernameOne = [];
                let arrayIndexesOfUsernameTwo = [];
                let arrayIndexesOfWinsOne = [];
                let arrayIndexesOfWinsTwo = [];

                arrayIndexesOfUsernameOne = getIndexes(statsMsg, ",");
                arrayIndexesOfUsernameTwo = getIndexes(statsMsg, ".");

                arrayIndexesOfWinsOne = getIndexes(statsMsg, "/");
                arrayIndexesOfWinsTwo = getIndexes(statsMsg, ":");

                for (var i = 0; i <= numThing; i++)
                {
                    let winsTableVal = parseInt(statsMsg.substring(arrayIndexesOfWinsOne[i]+1, arrayIndexesOfWinsTwo[i]));
                    //console.log(winsTableVal);
                    let userTableVal = statsMsg.substring(arrayIndexesOfUsernameOne[i]+1, arrayIndexesOfUsernameTwo[i]);
                    //console.log(userTableVal);
                    tableOfBruhStats.push({name: userTableVal, value: winsTableVal});
                    //[myid,jaron.40/0:1;1-0] or [id,username.elo/wins:losses;games-winstreak]
                }

                let stringForVal = "";
                let stringForUser = "";
                tableOfBruhStats.sort(compareNum);
                //console.log("Compared~!");
                for (var i = 0; i < numThing; i++)
                {
                    if (i < 10)
                    {
                        //console.log(tableOfBruhStats[i]);
                        //console.log(i);
                        stringForVal += "\n"+tableOfBruhStats[i].value;
                        stringForUser += "\n"+(i+1)+". "+tableOfBruhStats[i].name+": "+tableOfBruhStats[i].value;
                    }
                }
                message.channel.send({embed: {
                    color: 3457003,
                    title: "Top Wins: ",
                    fields: 
                    [
                        { name: "User: ", value: stringForUser, inline: true},
                        //{ name: "Wins: ", value: stringForVal, inline: true},
                    ]
                    }
                });
            } //wins
            else if(message.content.includes("wlr") == true)
            {
                //console.log("got inside wins");
                let tableOfBruhStats = [];
                let arrayIndexesOfUsernameOne = [];
                let arrayIndexesOfUsernameTwo = [];
                let arrayIndexesOfWinsOne = [];
                let arrayIndexesOfWinsTwo = [];
                let arrayIndexesOfLossesOne = [];
                let arrayIndexesOfLossesTwo = [];

                arrayIndexesOfUsernameOne = getIndexes(statsMsg, ",");
                arrayIndexesOfUsernameTwo = getIndexes(statsMsg, ".");

                arrayIndexesOfWinsOne = getIndexes(statsMsg, "/");
                arrayIndexesOfWinsTwo = getIndexes(statsMsg, ":");
                arrayIndexesOfLossesOne = getIndexes(statsMsg, ":");
                arrayIndexesOfLossesTwo = getIndexes(statsMsg, ";");

                for (var i = 0; i <= numThing; i++)
                {
                    let winsTableVal = parseInt(statsMsg.substring(arrayIndexesOfWinsOne[i]+1, arrayIndexesOfWinsTwo[i]));
                    let lossesTableVal = parseInt(statsMsg.substring(arrayIndexesOfLossesOne[i]+1, arrayIndexesOfLossesTwo[i]));
                    //console.log(winsTableVal);
                    let userTableVal = statsMsg.substring(arrayIndexesOfUsernameOne[i]+1, arrayIndexesOfUsernameTwo[i]);
                    //console.log(userTableVal);
                    if (winsTableVal/lossesTableVal == Number.POSITIVE_INFINITY)
                    {
                        tableOfBruhStats.push({name: userTableVal, value: winsTableVal});
                    }
                    else
                    {
                        tableOfBruhStats.push({name: userTableVal, value: ((winsTableVal/lossesTableVal).toFixed(2))});
                    }
                    //[myid,jaron.40/0:1;1-0] or [id,username.elo/wins:losses;games-winstreak]
                }

                let stringForVal = "";
                let stringForUser = "";

                tableOfBruhStats.sort(compareNum);
                //console.log("Compared~!");
                for (var i = 0; i < numThing; i++)
                {
                    if (i < 10)
                    {
                        //console.log(tableOfBruhStats[i]);
                        //console.log(i);
                        stringForVal += "\n"+tableOfBruhStats[i].value;
                        stringForUser += "\n"+(i+1)+". "+tableOfBruhStats[i].name+": "+tableOfBruhStats[i].value;
                    }
                }
                message.channel.send({embed: {
                    color: 3457003,
                    title: "Top Win/Loss Ratio: ",
                    fields: 
                    [
                        { name: "User: ", value: stringForUser, inline: true},
                        //{ name: "WLR: ", value: stringForVal, inline: true},
                    ]
                    }
                });
            } //wlr
            else if(message.content.includes("games") == true)
            {
                //console.log("got inside wins");
                let tableOfBruhStats = [];
                let arrayIndexesOfUsernameOne = [];
                let arrayIndexesOfUsernameTwo = [];
                let arrayIndexesOfGamesOne = [];
                let arrayIndexesOfGamesTwo = [];

                arrayIndexesOfUsernameOne = getIndexes(statsMsg, ",");
                arrayIndexesOfUsernameTwo = getIndexes(statsMsg, ".");

                arrayIndexesOfGamesOne = getIndexes(statsMsg, ";");
                arrayIndexesOfGamesTwo = getIndexes(statsMsg, "-");

                for (var i = 0; i <= numThing; i++)
                {
                    let gamesTableVal = parseInt(statsMsg.substring(arrayIndexesOfGamesOne[i]+1, arrayIndexesOfGamesTwo[i]));
                    //console.log(winsTableVal);
                    let userTableVal = statsMsg.substring(arrayIndexesOfUsernameOne[i]+1, arrayIndexesOfUsernameTwo[i]);
                    //console.log(userTableVal);
                    tableOfBruhStats.push({name: userTableVal, value: gamesTableVal});
                    //[myid,jaron.40/0:1;1-0] or [id,username.elo/wins:losses;games-winstreak]
                }

                let stringForVal = "";
                let stringForUser = "";
                tableOfBruhStats.sort(compareNum);
                //console.log("Compared~!");
                for (var i = 0; i < numThing; i++)
                {
                    if (i < 10)
                    {
                        //console.log(tableOfBruhStats[i]);
                        //console.log(i);
                        stringForVal += "\n"+tableOfBruhStats[i].value;
                        stringForUser += "\n"+(i+1)+". "+tableOfBruhStats[i].name+": "+tableOfBruhStats[i].value;
                    }
                }
                message.channel.send({embed: {
                    color: 3457003,
                    title: "Most Games Played: ",
                    fields: 
                    [
                        { name: "User: ", value: stringForUser, inline: true},
                        //{ name: "Games played: ", value: stringForVal, inline: true},
                    ]
                    }
                });
            } //games
            else if(message.content.includes("ws") == true)
            {
                //console.log("got inside wins");
                let tableOfBruhStats = [];
                let arrayIndexesOfUsernameOne = [];
                let arrayIndexesOfUsernameTwo = [];
                let arrayIndexesOfWSOne = [];
                let arrayIndexesOfWSTwo = [];

                arrayIndexesOfUsernameOne = getIndexes(statsMsg, ",");
                arrayIndexesOfUsernameTwo = getIndexes(statsMsg, ".");

                arrayIndexesOfWSOne = getIndexes(statsMsg, "-");
                arrayIndexesOfWSTwo = getIndexes(statsMsg, "]");

                for (var i = 0; i <= numThing; i++)
                {
                    let wsTableVal = parseInt(statsMsg.substring(arrayIndexesOfWSOne[i]+1, arrayIndexesOfWSTwo[i]));
                    //console.log(winsTableVal);
                    let userTableVal = statsMsg.substring(arrayIndexesOfUsernameOne[i]+1, arrayIndexesOfUsernameTwo[i]);
                    //console.log(userTableVal);
                    tableOfBruhStats.push({name: userTableVal, value: wsTableVal});
                    //[myid,jaron.40/0:1;1-0] or [id,username.elo/wins:losses;games-winstreak]
                }

                let stringForVal = "";
                let stringForUser = "";
                tableOfBruhStats.sort(compareNum);
                //console.log("Compared~!");
                for (var i = 0; i < numThing; i++)
                {
                    if (i < 10)
                    {
                        //console.log(tableOfBruhStats[i]);
                        //console.log(i);
                        stringForVal += "\n"+tableOfBruhStats[i].value;
                        stringForUser += "\n"+(i+1)+". "+tableOfBruhStats[i].name+": "+tableOfBruhStats[i].value;
                    }
                }
                message.channel.send({embed: {
                    color: 3457003,
                    title: "Highest Ongoing Winstreak: ",
                    fields: 
                    [
                        { name: "User: ", value: stringForUser, inline: true},
                        //{ name: "Winstreak: ", value: stringForVal, inline: true},
                    ]
                    }
                });
            } //ws
            else
            {
                //console.log("got inside wins");
                let tableOfBruhStats = [];
                let arrayIndexesOfUsernameOne = [];
                let arrayIndexesOfUsernameTwo = [];
                let arrayIndexesOfELOOne = [];
                let arrayIndexesOfELOTwo = [];

                arrayIndexesOfUsernameOne = getIndexes(statsMsg, ",");
                arrayIndexesOfUsernameTwo = getIndexes(statsMsg, ".");

                arrayIndexesOfELOOne = getIndexes(statsMsg, ".");
                arrayIndexesOfELOTwo = getIndexes(statsMsg, "/");

                for (var i = 0; i <= numThing; i++)
                {
                    let elowTableVal = parseInt(statsMsg.substring(arrayIndexesOfELOOne[i]+1, arrayIndexesOfELOTwo[i]));
                    //console.log(winsTableVal);
                    let userTableVal = statsMsg.substring(arrayIndexesOfUsernameOne[i]+1, arrayIndexesOfUsernameTwo[i]);
                    //console.log(userTableVal);
                    tableOfBruhStats.push({name: userTableVal, value: elowTableVal});
                    //[myid,jaron.40/0:1;1-0] or [id,username.elo/wins:losses;games-winstreak]
                }

                let stringForVal = "";
                let stringForUser = "";
                tableOfBruhStats.sort(compareNum);
                //console.log("Compared~!");
                for (var i = 0; i < numThing; i++)
                {
                    if (i < 10)
                    {
                        //console.log(tableOfBruhStats[i]);
                        //console.log(i);
                        stringForVal += "\n"+tableOfBruhStats[i].value;
                        stringForUser += "\n"+(i+1)+". "+tableOfBruhStats[i].name+": "+tableOfBruhStats[i].value;
                    }
                }
                message.channel.send({embed: {
                    color: 3457003,
                    title: "Top Players (ELO): ",
                    fields: 
                    [
                        { name: "User: ", value: stringForUser, inline: true}, //remove the stringforval if it fails.
                        //{ name: "ELO: ", value: stringForVal, inline: true},
                    ]
                    }
                });
            } //elo
        });
    }
    else if(command == 'winners')
    {
        message.channel.send("There haven't been any season champions yet, but stay tuned!");
    }
    else if(command == 'help')
    {
        message.channel.send({embed: {
            color: 3457003,
            title: "All commands",
            fields: 
            [
                { name: "help", value: "Displays all commands", inline: true},
                { name: "play", value: "Start a new queue", inline: true},
                { name: "2/4/6/8", value: "Set the total player count of the queue", inline: true},
                { name: "join/j", value: "Join a queue", inline: true},
                { name: "leave/l", value: "Leave a queue", inline: true},
                { name: "queue/q", value: "View all queued players", inline: true},
                { name: "pick", value: "Picks a player to join your team (Captains only)", inline: true},
                { name: "maps", value: "Lists maps currently in rotation", inline: true},
                { name: "season", value: "Lists all the banned items for the current season", inline: true},
                { name: "rules", value: "Description of player roles for Casual Ranked BW", inline: true},
                { name: "stats", value: "Shows your stats, and can show other players' stats by mentioning them", inline: true},
                { name: "lb (default elo, wins/wlr/games/ws)", value: "Lists the leaderboard for the top 10 players of each category", inline: true},
                { name: "winners", value: "Displays the past season's winners' stats", inline: true},
                { name: "score", value: "For jaron only to score games", inline: true},
                { name: "end", value: "jaron only", inline: true},
            ]
          }
        });
    }
    /*
        --
        TESTING PURPOSES COMMANDS - jaron ONLY
        --
    */
    else if(command == 'msg')
    {
        //eloChannel.messages.fetch("795693829360975913").then(message => message.edit("%")).catch(console.error).toString();
        message.channel.send(8);
    } 
    else if(command == 'gkv')
    {
        var omgRemaining = ["Greepu", "Mysto", "Diamond", "Luke", "Toekeo", "Gkv"];
        var omgCapOne = "Syd";
        var omgCapTwo = "Flipchuck";
        for (var j = 0; j < 6; j++)
        {
            var omgStringremain = "";
            for (var i = 0; i < omgRemaining.length; i++)
            {                           
                if(omgRemaining[i] != omgCapOne && omgRemaining[i] != omgCapTwo)
                {
                    omgStringremain += ", "+omgRemaining[i];
                }
            }
            omgStringremain = omgStringremain.substring(2);
            message.channel.send("Remaining players: "+omgStringremain);
            var omgBruh = Math.random()*omgRemaining.length;
            while (omgRemaining[omgBruh] === omgCapOne || omgRemaining[omgBruh] === omgCapTwo)
            {
                omgBruh = Math.random()*omgRemaining.length;
            } 
            omgRemaining.splice(omgBruh, 1);
        }
    }
}
);

client.login('NOT TODAY BUDDY!');
