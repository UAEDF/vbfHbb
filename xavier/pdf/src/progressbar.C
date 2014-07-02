/*  PROGRESSBAR.CPP
 *
 *  defines a simple progressbar to use in for loops. 
 *  
 *  author: Romeo Van Snick
 *  e-mail: romeo.vansnick@student.ua.ac.be
 *
 */


#include "progressbar.h"

// create a generic progressbar 
// please don't do this because you'll need to set the total anyway.
progressbar::progressbar()
{
	step=0;
	total=20;
	width=20;
	enabled=true;
	completed = false;
	std::cout << "A progressbar was created without any options."
			  << "This is possible, but the options will most likely be wrong." 
			  << std::endl;
}

// create a progressbar with total number of steps T and width W
progressbar::progressbar(const int T, const int W)
{
	step=0;
	enabled=true;
	completed=false;
	enabled = true;

	// dont't set total or width to lower than 2
	try{
		if ( T <= 1 )
		{
			total=20;
			throw 1;
		}else
		{
			total=T;
		}

		if ( W <= 1 )
		{
			width=20;
			throw 1;
		}else
		{
			width=W;
		}
	}
	catch(int err)
	{
		std::cout 	<< "Error: cannot set progressbar total or width"
					<< "to a number smaller than 2. Setting it to 20." 
					<< std::endl;
	}
}

void progressbar::enable()
{
	enabled = true;
}

void progressbar::disable()
{
	enabled = false;
}

void progressbar::settotal(const int t)
{
	total = t;
}

void progressbar::print(const char* msg)
{
	std::string testin(msg);
	std::string test("");

	if ( testin.compare(test) !=0 )
	{
		mesg = std::string(msg);
	}

	// only print if we haven't completed the progressbar yet
	// or if it has been enabled
	if (!completed && enabled)
	{
		// if step is not 0% or 100%, print a number of blocks,
		// proportional to the width of the progressbar.
		if ( ( step < total ) && (step > 0 ) )
		{
			// first calculate how many blocks we need
			double blocks = step;
			blocks = floor(blocks/total*width);

			// put the blocks in a string and create an opposite string of spaces
			std::string str1(blocks,'=');
			std::string str2(width-blocks-1,' ');

			// calculate the percentage
			double per = step;
			per = round(per/total*99);

			// save the old precision
			int old_prec = std::cout.precision();

			// put this all on the screen
			std::cout 	<< "\r" 
						<< std::setprecision(2) 
						<< std::setw(3)  << per 
						<< "\% [\033[34m" <<  str1 
						<< "\033[34;1m>\033[0m"<< str2 
						<< "] " << mesg << "\033[K"
						<< std::flush;

			// reset old precision
			std::cout.precision(old_prec);
		}
		// if the progress is at 0% print empty bar
		else if (step == 0)
		{
			// is step is zero, just print an empty bar
			std::string str(width,' ');
			std::cout << "  0\% [" << str << "] " << mesg << std::flush;
		}
		else if (step == total)
		{
			// set the completed flag to true
			completed=true;

			// if step equals total, print a full bar (green!).
			std::string str(width,'=');
			
			// save the old precision
			int old_prec = std::cout.precision();

			std::cout 	<< "\r100\% [\033[32;1m" 
						<< str << "\033[0m] " << mesg << "\033[K"
						<< std::flush << std::endl;
			
			// reset old precision
			std::cout.precision(old_prec);
		}
	}

}

void progressbar::print()
{
	print("");
}

// this just adds 1 to the step member, but makes sure wo don't go over width.
void progressbar::progress()
{
	step++;
	if (step > total)
	{
		std::cout 	<< "Warning: steps of progressbar are getting bigger than "
					<< "total, this should not happen.\n"
				 	<< "         Fixing this will also fix the fatal string "
					<< "length_error below." 
					<< std::endl;
	}
}

// easy as heck, set step to 0
void progressbar::reset()
{
	step=0;
	mesg=std::string("");
	completed = false;
}

// When a progess fails, show a red progressbar
void progressbar::fail()
{
	fail("");
}

// When a progess fails, show a red progressbar and a message
void progressbar::fail(const char* msg)
{
	if ( !completed && enabled )
	{
		// a failed progressbar cannot progress further,
		// thus we set the completed flag
		completed = true;
		// first calculate how many blocks we need
		double blocks = step-1;
		blocks = floor(blocks/total*width);

		// put the blocks in a string and create an opposite string of spaces
		std::string str1(blocks,'=');
		std::string str2(width - blocks - 1,' ');

		// calculate the percentage
		double per = step;
		per = round(per/total*99);

		// save the old precision
		int old_prec = std::cout.precision();
		
		// put this all on the screen, in red, width msg as message
		std::cout	<< "\r"
					<< std::setw(3) 
					<< std::setprecision(2) 
					<< per << "\% [\033[31m" 
					<< str1 << "\033[31;1mx\033[0m"
					<< str2 << "] "
					<< msg  << std::flush << std::endl;
		
		// reset old precision
		std::cout.precision(old_prec);
	}
}

// closing a progressbar just adds a newline
void progressbar::close()
{
	if ( enabled )
	{
		std::cout << std::endl;
	}
}
